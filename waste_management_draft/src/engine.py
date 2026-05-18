# src/engine.py
# Module: Simulation Engine
# Purpose: Orchestrates the full waste collection lifecycle.
# Flow: Monitor Bins -> Rank by Priority -> Allocate Vehicles -> Allocate Facilities

from monitoring import WasteMonitor
from priority import PriorityScoring
from vehicle_allocation import VehicleAllocator
from facility_allocation import FacilityAllocator

class SimulationEngine:
    """
    Central coordinator for the WasteWise system.
    Connects monitoring, priority scoring, vehicle dispatch,
    and facility routing into a single simulation loop.
    """

    def __init__(self, bins, vehicles, facilities, distance_graph):
        self.bins = bins
        self.vehicles = vehicles
        self.facilities = facilities
        self.graph = distance_graph

        # Initialize all sub-modules
        self.monitor = WasteMonitor(bins)
        self.priority_scorer = PriorityScoring()
        self.vehicle_allocator = VehicleAllocator(vehicles)
        self.facility_allocator = FacilityAllocator(facilities)

        # Event log for the current simulation run
        self.event_log = []

    def log_event(self, event_type, message, details=None):
        """Records a simulation event for the GUI/reports."""
        entry = {
            "type": event_type,
            "message": message,
            "details": details or {}
        }
        self.event_log.append(entry)
        print(f"[{event_type}] {message}")

    # ------------------------------------------------------------------
    #  STEP 1: Add waste to a bin (called by user input or Phase 1)
    # ------------------------------------------------------------------
    def add_waste(self, bin_id, waste_type, quantity, user_id=None):
        """
        Adds waste to a specific bin and logs the event.
        This is the entry point that Phase 1's InputProcessor will call.
        """
        result = self.monitor.add_waste_to_bin(bin_id, waste_type, quantity)

        if result and result.get("success"):
            self.log_event(
                "DISPOSAL",
                f"User {user_id or 'UNKNOWN'} added {quantity}kg of {waste_type} to Bin {bin_id}.",
                {"bin_id": bin_id, "waste_type": waste_type, "quantity": quantity,
                 "fill_pct": result["fill_percentage"]}
            )
            # Run check immediately on disposal
            bin_obj = self.monitor.find_bin(bin_id)
            if bin_obj:
                from emergency import emergency_handler
                emergency_handler.check_emergency_conditions(bin_obj)
        return result

    # ------------------------------------------------------------------
    #  STEP 2: Run the full optimization cycle
    # ------------------------------------------------------------------
    def run_optimization(self, alert_threshold=80.0):
        """
        Executes one full optimization cycle:
        1. Detect bins approaching capacity.
        2. Rank them by priority.
        3. Assign vehicles to the highest-priority bins.
        4. Route loaded vehicles to facilities.
        
        Returns:
            A summary dict of what happened during this cycle.
        """
        summary = {
            "bins_detected": 0,
            "bins_collected": 0,
            "vehicles_dispatched": 0,
            "vehicles_unloaded": 0,
            "failed_allocations": []
        }

        # --- Phase A: Detect & Rank ---
        from emergency import emergency_handler
        
        # Check and flag emergency situations for all bins
        for b in self.bins:
            emergency_handler.check_emergency_conditions(b)

        self.log_event("SCAN", f"Scanning for bins above {alert_threshold}% capacity...")
        alert_bins = self.monitor.get_bins_approaching_capacity(alert_threshold)
        
        # Guarantee all active emergency bins are included in the dispatch alert list
        for b in self.bins:
            if getattr(b, 'is_emergency', False) and b not in alert_bins:
                alert_bins.append(b)
                
        summary["bins_detected"] = len(alert_bins)

        if not alert_bins:
            self.log_event("SCAN", "No bins require attention. System is healthy.")
            return summary

        self.log_event("SCAN", f"Found {len(alert_bins)} bin(s) approaching capacity.")

        ranked = self.priority_scorer.rank_bins(alert_bins)
        self.log_event("PRIORITY", "Bins ranked by urgency:")
        for bin_obj, score in ranked:
            prefix = "[EMERGENCY] " if getattr(bin_obj, 'is_emergency', False) else ""
            self.log_event("PRIORITY", f"  {prefix}{bin_obj.bin_id} -> Score: {score:.1f} "
                           f"(Fill: {bin_obj.get_fill_percentage():.0f}%, "
                           f"Type: {bin_obj.waste_type}, Source: {bin_obj.source_type})")

        # --- Phase B: Assign Vehicles ---
        self.log_event("DISPATCH", "Assigning vehicles to bins...")
        collection_pairs = []  # (vehicle, bin) pairs that succeeded

        for bin_obj, score in ranked:
            if getattr(bin_obj, 'is_emergency', False):
                self.log_event("EMERGENCY", f"[EMERGENCY DISPATCH] FOR BIN {bin_obj.bin_id}: {bin_obj.emergency_reason}")

            vehicle = self.vehicle_allocator.allocate_vehicle(bin_obj, self.graph)

            if vehicle is None:
                msg = f"No suitable vehicle available for Bin {bin_obj.bin_id} ({bin_obj.waste_type})."
                self.log_event("DISPATCH", f"  FAILED: {msg}")
                summary["failed_allocations"].append(bin_obj.bin_id)
                # Increment failed collection attempts to potentially trigger emergency status later
                bin_obj.failed_collection_attempts = getattr(bin_obj, 'failed_collection_attempts', 0) + 1
                continue

            # Perform the collection
            self.log_event("COLLECT", f"  Vehicle {vehicle.vehicle_id} -> Bin {bin_obj.bin_id} "
                           f"({bin_obj.waste_type}, {bin_obj.fill_level:.1f}kg)")
            
            # Track assignment for GUI visibility
            vehicle.current_task = "Collecting"
            vehicle.current_target = bin_obj.bin_id
            bin_obj.assigned_vehicle = vehicle.vehicle_id
            
            is_emergency_active = getattr(bin_obj, 'is_emergency', False)
            
            self.vehicle_allocator.update_allocation(vehicle, bin_obj)
            self.monitor.clear_bin(bin_obj.bin_id)
            
            # Resolve emergency logs and attributes if this bin was flagged
            if is_emergency_active:
                emergency_handler.resolve_emergency(bin_obj, vehicle.vehicle_id)
                self.log_event("EMERGENCY", f"[EMERGENCY RESOLVED] Bin {bin_obj.bin_id} by Vehicle {vehicle.vehicle_id}.")
            
            # Record last action for GUI persistence
            vehicle.last_task = "Collected"
            vehicle.last_target = bin_obj.bin_id
            
            # Reset bin assignment after clearing
            bin_obj.assigned_vehicle = None
            
            collection_pairs.append((vehicle, bin_obj))
            summary["bins_collected"] += 1
            summary["vehicles_dispatched"] += 1

        # --- Phase C: Route Vehicles to Facilities ---
        self.log_event("ROUTE", "Routing loaded vehicles to processing facilities...")

        # Check EVERY vehicle in the fleet to see if it needs unloading
        for vehicle in self.vehicles:
            if vehicle.current_load > 0:
                facility = self.facility_allocator.allocate_facility(vehicle, self.graph)

                if facility is None:
                    continue

                # Set routing task for visibility
                vehicle.current_task = "Routing"
                vehicle.current_target = facility.facility_id

                # Unload at facility
                success = self.facility_allocator.process_vehicle_unload(vehicle, facility)
                if success:
                    summary["vehicles_unloaded"] += 1
                    self.log_event("UNLOAD", f"  Vehicle {vehicle.vehicle_id} -> "
                                   f"Facility {facility.facility_id} "
                                   f"({facility.facility_type})")

        # --- Summary ---
        self.log_event("COMPLETE", f"Optimization cycle complete. "
                       f"Collected: {summary['bins_collected']}, "
                       f"Unloaded: {summary['vehicles_unloaded']}, "
                       f"Failed: {len(summary['failed_allocations'])}")
        return summary

    def advance_facilities(self):
        """Advances the processing timer for all facilities."""
        for f in self.facilities:
            status = f.tick()
            if status == "emptied":
                self.log_event("FACILITY", f"Facility {f.facility_id} processing complete. Load cleared.")
            elif status == "low_load":
                self.log_event("FACILITY", f"Facility {f.facility_id} waiting for more waste (below threshold).",
                               {"load_pct": (f.current_load / f.max_daily_capacity * 100)})

    def get_system_status(self):
        """Returns a full snapshot of the system for GUI display."""
        return {
            "bins": self.monitor.get_all_bin_statuses(),
            "vehicles": self.vehicle_allocator.get_vehicle_statuses(),
            "facilities": self.facility_allocator.get_facility_statuses(),
            "event_log": self.event_log[-20:]  # Last 20 events
        }

    def reset_all(self):
        """Resets every entity to its initial state for re-running."""
        for b in self.bins:
            b.reset()
        for v in self.vehicles:
            v.reset()
        for f in self.facilities:
            f.reset()
        self.event_log.clear()
        self.log_event("SYSTEM", "All entities have been reset.")

# src/facilities/facility_allocation.py
# Handles routing vehicles to processing facilities, failover redirection, and status reporting

from utils import logger

class FacilityAllocator:
    """Handles routing vehicles to the correct processing facility with automated failover."""
    
    def __init__(self, facilities):
        self.facilities = facilities  # List of Facility objects

    def get_partner_facility(self, facility):
        """
        Finds the redundant backup partner for a given facility.
        A partner is another facility of the same type (same facility_type)
        that is currently active and has remaining capacity.
        
        Returns:
            The partner Facility object, or None if no active partner found.
        """
        for f in self.facilities:
            if (f.facility_id != facility.facility_id 
                and f.facility_type == facility.facility_type 
                and f.is_active):
                return f
        return None

    def reroute_waste_on_shutdown(self, shut_down_facility):
        """
        When a facility is shut down, automatically reroute its current load
        to the active partner facility of the same type.
        
        Returns:
            The partner facility that received the rerouted waste, or None if no partner available.
        """
        if shut_down_facility.current_load <= 0:
            return None
            
        partner = self.get_partner_facility(shut_down_facility)
        if partner is None:
            logger.log_facility_event(
                shut_down_facility.facility_id, 
                "FAILOVER_FAILED", 
                f"No active partner facility available for {shut_down_facility.facility_type}! "
                f"{shut_down_facility.current_load:.1f}kg of waste stranded."
            )
            print(f"[FAILOVER WARNING] Facility {shut_down_facility.facility_id} shut down with "
                  f"{shut_down_facility.current_load:.1f}kg but no partner available!")
            return None
        
        rerouted_amount = shut_down_facility.current_load
        remaining_at_partner = partner.max_daily_capacity - partner.current_load
        
        # Transfer as much as possible to the partner
        transfer_amount = min(rerouted_amount, remaining_at_partner)
        partner.current_load += transfer_amount
        shut_down_facility.current_load -= transfer_amount
        
        shut_down_facility.redirected_count += 1
        
        logger.log_facility_event(
            shut_down_facility.facility_id, 
            "FAILOVER_REROUTE", 
            f"Rerouted {transfer_amount:.1f}kg to partner facility {partner.facility_id} "
            f"({partner.facility_type})",
            redirected_to=partner.facility_id
        )
        print(f"[FAILOVER] {transfer_amount:.1f}kg rerouted from {shut_down_facility.facility_id} "
              f"to {partner.facility_id} ({partner.facility_type})")
        
        if shut_down_facility.current_load > 0:
            print(f"[FAILOVER WARNING] Partner {partner.facility_id} at capacity! "
                  f"{shut_down_facility.current_load:.1f}kg remains stranded at {shut_down_facility.facility_id}.")
        
        return partner

    def allocate_facility(self, vehicle, distance_graph=None):
        """
        Finds the best active facility for a vehicle to unload its waste.
        If the primary closest facility is inactive or at capacity, fails over
        to the next best active facility.
        
        Selection criteria:
        1. Facility must be active.
        2. Facility must support the vehicle's collected waste type.
        3. Facility must have enough remaining capacity for the vehicle's load.
        4. If a graph is provided, prefer the nearest facility.
        
        Returns:
            The best matching Facility object, or None if no valid facility found.
        """
        if vehicle.collected_waste_type is None and vehicle.current_load == 0:
            return None

        waste_type = vehicle.collected_waste_type
        load_amount = vehicle.current_load

        # Find nearest facility regardless of active state first, to track failovers
        primary_facility = None
        min_dist_primary = float('inf')
        
        for f in self.facilities:
            if waste_type in f.supported_waste_types and (f.current_load + load_amount) <= f.max_daily_capacity:
                if distance_graph:
                    dist = distance_graph.shortest_distance(vehicle.location_id, f.location_id)
                    if dist < min_dist_primary:
                        min_dist_primary = dist
                        primary_facility = f
                else:
                    primary_facility = f
                    break

        # Now select the best active facility
        best_active_facility = None
        min_distance = float('inf')

        for facility in self.facilities:
            # Must be active and able to process
            if facility.is_active and facility.can_process(waste_type, load_amount):
                if distance_graph:
                    dist = distance_graph.shortest_distance(vehicle.location_id, facility.location_id)
                    if dist < min_distance:
                        min_distance = dist
                        best_active_facility = facility
                else:
                    best_active_facility = facility
                    break

        # Handle failover tracking
        if primary_facility and not primary_facility.is_active:
            if best_active_facility:
                primary_facility.redirected_count += 1
                logger.log_facility_event(
                    primary_facility.facility_id, 
                    "FAILOVER_REDIRECT", 
                    f"Redirected {load_amount:.1f}kg due to high emissions/inactivity",
                    redirected_to=best_active_facility.facility_id
                )
                print(f"[FAILOVER] Facility {primary_facility.facility_id} inactive! "
                      f"Redirecting waste to {best_active_facility.facility_id} ({best_active_facility.facility_type})")
            else:
                print(f"[FAILOVER WARNING] Facility {primary_facility.facility_id} inactive and no active alternative found!")

        return best_active_facility

    def process_vehicle_unload(self, vehicle, facility):
        """
        Unloads waste from a vehicle into the facility.
        Updates both the vehicle and facility state.
        
        Returns:
            True if unloading succeeded, False otherwise.
        """
        if vehicle is None or facility is None:
            return False

        waste_type = vehicle.collected_waste_type
        load_amount = vehicle.current_load

        if facility.receive_waste(waste_type, load_amount):
            print(f"  Vehicle {vehicle.vehicle_id} unloaded {load_amount:.1f}kg of "
                  f"{waste_type} at {facility.facility_id}.")
            
            # If the facility got deactivated due to emissions during this unload,
            # automatically reroute its accumulated load to the partner
            if not facility.is_active:
                partner = self.reroute_waste_on_shutdown(facility)
                if partner:
                    print(f"  [AUTO-FAILOVER] Facility {facility.facility_id} exceeded emissions! "
                          f"Load auto-rerouted to {partner.facility_id}.")
                          
            # --- Segregation Logic ---
            if facility.facility_type == "Segregation Unit":
                print(f"  [SEGREGATION] Segregating {load_amount:.1f}kg of mixed waste from {vehicle.vehicle_id}...")
                
                # Active plants
                all_active_primary = [f for f in self.facilities if f.is_active and f.facility_type != "Segregation Unit"]
                
                # Iterate over exact composition
                for category, weight in vehicle.waste_composition.items():
                    if weight <= 0:
                        continue
                        
                    # Find all facilities that support this specific category
                    target_plants = [f for f in all_active_primary if category in f.supported_waste_types]
                    
                    if target_plants:
                        # Distribute this exact category weight evenly among its specialized facilities
                        amount_per_plant = weight / len(target_plants)
                        for target_plant in target_plants:
                            if target_plant.receive_waste(category, amount_per_plant):
                                print(f"    -> Sent {amount_per_plant:.1f}kg (Exact: {category}) to {target_plant.facility_id} ({target_plant.facility_type})")
                    else:
                        print(f"    -> WARNING: No active facility available to process {weight:.1f}kg of {category}!")
                        
                # Log process completion per user request
                logger.log_facility_event(
                    facility.facility_id,
                    "SEGREGATION_COMPLETE",
                    f"Processed and segregated {load_amount:.1f}kg of waste precisely."
                )
                        
                # Deduct the load from segregation unit since it's been instantly forwarded
                facility.current_load = max(0.0, facility.current_load - load_amount)
            # -------------------------
            
            # Reset vehicle after successful unloading
            vehicle.current_load = 0.0
            vehicle.collected_waste_type = None
            vehicle.assigned_facility = None
            vehicle.location_id = facility.location_id
            vehicle.last_task = "Unloaded"
            vehicle.last_target = facility.facility_id
            vehicle.current_task = "Idle"
            vehicle.current_target = "N/A"
            vehicle.is_available = True
            return True
        else:
            print(f"  ERROR: Facility {facility.facility_id} cannot accept "
                  f"{load_amount:.1f}kg of {waste_type}.")
            return False

    def get_facility_statuses(self):
        """Returns a summary of all facility states for the GUI/reports."""
        statuses = []
        for f in self.facilities:
            # Find this facility's partner for status display
            partner = self.get_partner_facility(f)
            partner_id = partner.facility_id if partner else "NONE"
            
            statuses.append({
                "facility_id": f.facility_id,
                "facility_type": f.facility_type,
                "current_load": round(f.current_load, 1),
                "max_capacity": f.max_daily_capacity,
                "remaining": round(f.get_remaining_capacity(), 1),
                "waste_types": f.supported_waste_types,
                "location_id": f.location_id,
                "is_active": f.is_active,
                "emissions": round(f.emissions, 2),
                "redirected_count": f.redirected_count,
                "partner_facility": partner_id
            })
        return statuses

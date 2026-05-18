# src/facilities/facility_allocation.py
# Handles routing vehicles to processing facilities, failover redirection, and status reporting

from utils import logger

class FacilityAllocator:
    """Handles routing vehicles to the correct processing facility with automated failover."""
    
    def __init__(self, facilities):
        self.facilities = facilities  # List of Facility objects

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
                print(f"[FAILOVER] Facility {primary_facility.facility_id} inactive! Redirecting waste to {best_active_facility.facility_id}")
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
                "redirected_count": f.redirected_count
            })
        return statuses

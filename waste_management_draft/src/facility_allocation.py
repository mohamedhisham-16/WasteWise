# src/facility_allocation.py
# Module: Facility Allocation Module
# Purpose: Route vehicles carrying collected waste to appropriate processing facilities.

class FacilityAllocator:
    """Handles routing vehicles to the correct processing facility."""
    
    def __init__(self, facilities):
        self.facilities = facilities  # List of Facility objects

    def allocate_facility(self, vehicle, distance_graph=None):
        """
        Finds the best facility for a vehicle to unload its waste.
        
        Selection criteria:
        1. Facility must support the vehicle's collected waste type.
        2. Facility must have enough remaining capacity for the vehicle's load.
        3. If a graph is provided, prefer the nearest facility.
        
        Returns:
            The best matching Facility object, or None if no valid facility found.
        """
        if vehicle.collected_waste_type is None and vehicle.current_load == 0:
            return None

        waste_type = vehicle.collected_waste_type
        load_amount = vehicle.current_load

        best_facility = None
        min_distance = float('inf')

        for facility in self.facilities:
            # Check compatibility and capacity
            if facility.can_process(waste_type, load_amount):
                if distance_graph:
                    dist = distance_graph.shortest_distance(
                        vehicle.location_id, facility.location_id
                    )
                    if dist < min_distance:
                        min_distance = dist
                        best_facility = facility
                else:
                    # No graph, just return first compatible facility
                    return facility

        return best_facility

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
            # Vehicle stays available for next assignment
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
                "location_id": f.location_id
            })
        return statuses

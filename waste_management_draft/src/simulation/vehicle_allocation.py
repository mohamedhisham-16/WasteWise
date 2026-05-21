# src/vehicle_allocation.py
# Module: Vehicle Allocation Module
# Purpose: Assign compatible and available vehicles to bins needing collection.
# Uses Dijkstra's shortest path for optimal vehicle selection.

class VehicleAllocator:
    """Handles the assignment of vehicles to bin collection tasks."""
    
    def __init__(self, vehicles):
        self.vehicles = vehicles  # List of Vehicle objects

    def allocate_vehicle(self, bin_obj, distance_graph=None):
        """
        Finds the most suitable vehicle for a bin.
        
        Selection criteria (in order):
        1. Vehicle must be available.
        2. Vehicle must support the bin's waste type.
        3. Vehicle must have enough remaining capacity.
        4. If a graph is provided, pick the closest vehicle (by shortest path).
        """
        best_vehicle = None
        min_distance = float('inf')
        
        for vehicle in self.vehicles:
            # 1. Constraint: Compatibility & Capacity
            if vehicle.can_collect(bin_obj):
                # If we have a graph, use Dijkstra to find the closest vehicle
                if distance_graph:
                    dist = distance_graph.shortest_distance(
                        vehicle.location_id, bin_obj.location_id
                    )
                    if dist < min_distance:
                        min_distance = dist
                        best_vehicle = vehicle
                else:
                    # No graph provided, just pick the first available
                    return vehicle
        
        return best_vehicle

    def update_allocation(self, vehicle, bin_obj):
        """
        Processes the assignment: loads waste onto vehicle and moves it.
        
        Returns:
            True if successful, False otherwise.
        """
        if vehicle and bin_obj:
            # Calculate the weighted average contamination level for the whole load
            new_total = vehicle.current_load + bin_obj.fill_level
            if new_total > 0:
                current_contaminated = vehicle.current_load * vehicle.contamination_level
                added_contaminated = bin_obj.fill_level * getattr(bin_obj, 'contamination_level', 0.0)
                vehicle.contamination_level = (current_contaminated + added_contaminated) / new_total

            # Merge the exact waste composition dictionaries
            for cat, weight in getattr(bin_obj, 'waste_composition', {}).items():
                if cat not in vehicle.waste_composition:
                    vehicle.waste_composition[cat] = 0.0
                vehicle.waste_composition[cat] += weight

            vehicle.current_load += bin_obj.fill_level
            
            # Record the original expected waste type (before converting to mixed)
            if vehicle.original_waste_type is None:
                vehicle.original_waste_type = bin_obj.waste_type
                
            # Check contamination threshold to set or maintain "Mixed/Contaminated" type
            if getattr(bin_obj, 'contamination_level', 0.0) > 0.40 or vehicle.collected_waste_type == "Mixed/Contaminated":
                vehicle.collected_waste_type = "Mixed/Contaminated"
            else:
                vehicle.collected_waste_type = bin_obj.waste_type
                
            # Update location to the bin's location after collection
            vehicle.location_id = bin_obj.location_id
            print(f"  Vehicle {vehicle.vehicle_id} collected {bin_obj.fill_level:.1f}kg "
                  f"from Bin {bin_obj.bin_id}. Load: {vehicle.current_load:.1f}/{vehicle.total_capacity}")
            return True
        return False

    def get_available_vehicles(self):
        """Returns a list of all vehicles that are currently available."""
        return [v for v in self.vehicles if v.is_available]

    def get_vehicle_statuses(self):
        """Returns a summary of all vehicle states for the GUI/reports."""
        statuses = []
        for v in self.vehicles:
            statuses.append({
                "vehicle_id": v.vehicle_id,
                "vehicle_type": v.vehicle_type,
                "current_load": round(v.current_load, 1),
                "total_capacity": v.total_capacity,
                "is_available": v.is_available,
                "location_id": v.location_id,
                "waste_types": v.supported_waste_types,
                "current_task": v.current_task,
                "current_target": v.current_target,
                "last_task": v.last_task,
                "last_target": v.last_target
            })
        return statuses

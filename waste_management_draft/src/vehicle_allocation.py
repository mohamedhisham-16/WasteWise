# src/vehicle_allocation.py
# Module: Vehicle Allocation Module
# Purpose: Assign compatible and available vehicles to collected bins.

class VehicleAllocator:
    """Handles the assignment of vehicles to bin collection tasks."""
    
    def __init__(self, vehicles):
        self.vehicles = vehicles # List of Vehicle objects

    def allocate_vehicle(self, bin_obj, distance_graph=None):
        """Attempts to find the most suitable vehicle for a bin."""
        best_vehicle = None
        min_distance = float('inf')
        
        for vehicle in self.vehicles:
            # 1. Constraint: Compatibility & Capacity
            if vehicle.can_collect(bin_obj):
                # If we have a graph, try to find the closest vehicle
                if distance_graph:
                    dist = distance_graph.get_distance(vehicle.location_id, bin_obj.location_id)
                    if dist < min_distance:
                        min_distance = dist
                        best_vehicle = vehicle
                else:
                    # No graph provided, just pick the first available
                    return vehicle
        
        return best_vehicle

    def update_allocation(self, vehicle, bin_obj):
        """Processes the assignment, updating vehicle load and status."""
        if vehicle and bin_obj:
            vehicle.current_load += bin_obj.fill_level
            # Update location to the bin's location after collection
            vehicle.location_id = bin_obj.location_id
            return True
        return False

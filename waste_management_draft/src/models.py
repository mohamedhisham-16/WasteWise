# src/models.py
# This module defines the base classes for the Waste Management System.
# Each class represents a physical entity in the system.

class Bin:
    """Represents a waste collection point."""
    def __init__(self, bin_id, capacity, waste_type, source_type, location_id):
        self.bin_id = bin_id
        self.capacity = capacity  # Maximum capacity of the bin
        self.fill_level = 0.0     # Current fill level (in units)
        self.waste_type = waste_type  # e.g., 'Organic', 'Recyclable', 'Hazardous'
        self.source_type = source_type # e.g., 'Hospital', 'Apartment', 'Commercial'
        self.location_id = location_id # The ID of the node in the distance graph
        self.contamination_level = 0.0 # Percentage of incorrect waste mixed in

    def get_fill_percentage(self):
        """Calculates how full the bin is."""
        if self.capacity == 0:
            return 0
        return (self.fill_level / self.capacity) * 100

    def __repr__(self):
        return f"Bin({self.bin_id}, {self.waste_type}, {self.get_fill_percentage():.1f}%)"


class Vehicle:
    """Represents a waste collection truck."""
    def __init__(self, vehicle_id, vehicle_type, total_capacity, supported_waste_types, location_id):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type # e.g., 'Compactor', 'Hazardous Truck'
        self.total_capacity = total_capacity # Total weight/volume it can carry
        self.current_load = 0.0 # Current amount of waste being carried
        self.supported_waste_types = supported_waste_types # List of compatible waste types
        self.location_id = location_id # Current location in the graph
        self.is_available = True # Status (available or busy/broken down)

    def can_collect(self, bin_obj):
        """Checks if the vehicle is compatible with the bin's waste type and has capacity."""
        is_compatible = bin_obj.waste_type in self.supported_waste_types
        has_space = (self.current_load + bin_obj.fill_level) <= self.total_capacity
        return is_compatible and has_space and self.is_available

    def __repr__(self):
        return f"Vehicle({self.vehicle_id}, {self.vehicle_type}, Load: {self.current_load}/{self.total_capacity})"


class Facility:
    """Represents a waste processing plant."""
    def __init__(self, facility_id, facility_type, max_daily_capacity, supported_waste_types, current_load, location_id):
        self.facility_id = facility_id
        self.facility_type = facility_type # e.g., 'Recycling Plant', 'Compost Unit'
        self.max_daily_capacity = max_daily_capacity # Processing limit per day
        self.current_load = current_load # Amount of waste received today
        self.supported_waste_types = supported_waste_types # Compatibility
        self.location_id = location_id # Location node ID

    def can_process(self, waste_type, quantity):
        """Checks if the facility can handle the specific waste type and quantity."""
        is_compatible = waste_type in self.supported_waste_types
        has_capacity = (self.current_load + quantity) <= self.max_daily_capacity
        return is_compatible and has_capacity

    def __repr__(self):
        return f"Facility({self.facility_id}, {self.facility_type}, Capacity: {self.current_load}/{self.max_daily_capacity})"

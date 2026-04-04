# src/monitoring.py
# Module: Waste Monitoring Module
# Purpose: Track and update bin fill levels and status.

class WasteMonitor:
    """Manages the current state of bins and alerts when they approach capacity."""
    
    def __init__(self, bins):
        self.bins = bins # List of Bin objects

    def add_waste_to_bin(self, bin_id, waste_type, quantity):
        """
        Simulates a user adding a specific type/quantity of waste.
        Updates fill level and recalculates contamination automatically.
        """
        for b in self.bins:
            if b.bin_id == bin_id:
                # 1. Total Weight Update
                old_total = b.fill_level
                new_total = old_total + quantity
                
                if new_total > b.capacity:
                    print(f"ERROR: Cannot add {quantity}kg. Bin {bin_id} would overflow!")
                    return False

                # 2. Track 'Incorrect' Weight
                # We calculate how much of the OLD weight was incorrect
                old_incorrect_weight = old_total * b.contamination_level
                
                # Check if the NEWLY added waste is incorrect
                is_incorrect = (waste_type != b.waste_type)
                new_incorrect_added = quantity if is_incorrect else 0.0
                
                # 3. Update Bin Attributes
                b.fill_level = new_total
                total_incorrect = old_incorrect_weight + new_incorrect_added
                b.contamination_level = total_incorrect / new_total
                
                print(f"SUCCESS: Added {quantity}kg of {waste_type} to Bin {bin_id}.")
                print(f"  New Fill: {b.get_fill_percentage():.1f}% | New Contamination: {b.contamination_level*100:.1f}%")
                return True
        return False

    def get_bins_approaching_capacity(self, threshold=90.0):
        """Identifies bins that have exceeded a specific fill percentage."""
        alert_bins = []
        for bin_obj in self.bins:
            if bin_obj.get_fill_percentage() >= threshold:
                alert_bins.append(bin_obj)
        return alert_bins

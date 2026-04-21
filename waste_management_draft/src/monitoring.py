# src/monitoring.py
# Module: Waste Monitoring Module
# Purpose: Track and update bin fill levels and status.
# Works alongside Phase 1's InputProcessor for contamination/penalty tracking.
import random

class WasteMonitor:
    """Manages the current state of bins and alerts when they approach capacity."""
    
    def __init__(self, bins):
        self.bins = bins  # List of Bin objects

    def find_bin(self, bin_id):
        """Finds and returns a Bin object by its ID."""
        for b in self.bins:
            if b.bin_id == bin_id:
                return b
        return None

    def add_waste_to_bin(self, bin_id, waste_type, quantity):
        """
        Simulates a user adding a specific type/quantity of waste.
        Updates fill level and recalculates contamination automatically.
        
        Returns:
            dict with status info, or None if bin not found.
        """
        b = self.find_bin(bin_id)
        if b is None:
            print(f"ERROR: Bin {bin_id} not found.")
            return None

        # 1. Total Weight Update
        old_total = b.fill_level
        new_total = old_total + quantity
        
        if new_total > b.capacity:
            print(f"ERROR: Cannot add {quantity}kg. Bin {bin_id} would overflow!")
            return {"success": False, "reason": "overflow"}

        # 2. Automated Contamination Tracking
        # Simulate a smart sensor: 30% chance of detecting minor contamination
        contamination_pct = 0.0
        if random.random() < 0.3:
            contamination_pct = random.uniform(0.01, 0.08) # 1% to 8% contamination
            
        old_incorrect_weight = old_total * b.contamination_level
        new_incorrect_added = quantity * contamination_pct
        
        # 3. Update Bin Attributes
        b.fill_level = new_total
        total_incorrect = old_incorrect_weight + new_incorrect_added
        b.contamination_level = total_incorrect / new_total if new_total > 0 else 0.0
        
        print(f"SUCCESS: Added {quantity}kg of {waste_type} to Bin {bin_id}.")
        print(f"  System Detected: {contamination_pct*100:.1f}% contamination.")
        print(f"  New Total Fill: {b.get_fill_percentage():.1f}% | Total Contamination: {b.contamination_level*100:.1f}%")
        
        return {
            "success": True,
            "bin_id": bin_id,
            "fill_percentage": b.get_fill_percentage(),
            "contamination_detected": contamination_pct,
            "total_contamination": b.contamination_level
        }

    def get_bins_approaching_capacity(self, threshold=80.0):
        """Identifies bins that have exceeded a specific fill percentage."""
        alert_bins = []
        for bin_obj in self.bins:
            if bin_obj.get_fill_percentage() >= threshold:
                alert_bins.append(bin_obj)
        return alert_bins

    def get_all_bin_statuses(self):
        """Returns a summary list of all bins and their current state."""
        statuses = []
        for b in self.bins:
            statuses.append({
                "bin_id": b.bin_id,
                "waste_type": b.waste_type,
                "source_type": b.source_type,
                "fill_percentage": round(b.get_fill_percentage(), 1),
                "contamination": round(b.contamination_level * 100, 1),
                "location_id": b.location_id,
                "assigned_vehicle": b.assigned_vehicle
            })
        return statuses

    def clear_bin(self, bin_id):
        """Empties a bin after collection. Called by the engine after vehicle pickup."""
        b = self.find_bin(bin_id)
        if b:
            collected_amount = b.fill_level
            b.fill_level = 0.0
            b.contamination_level = 0.0
            print(f"  Bin {bin_id} cleared. {collected_amount:.1f}kg collected.")
            return collected_amount
        return 0.0

# src/simulation/input_processor.py
# Processes waste disposals by residents, contamination assessments, and warnings

import json
import os
import random
import uuid
from utils import constants, logger

def calculate_automated_contamination(quantity, severity_factor=0.05):
    """
    Simulates automated contamination detection.
    Returns a random contamination weight based on a severity factor.
    """
    chance = random.random()
    if chance < 0.3:  # 30% chance of contamination
        factor = random.uniform(0.01, severity_factor)
        return float(quantity * factor)
    return 0.0

def calculate_penalty(contamination_pct):
    """
    Calculates the penalty based on Option 4: Pure Percentage + Fixed Base Fee.
    Formula: ₹25 (Base Fine) + [Contamination % × ₹1]
    """
    if contamination_pct <= 0:
        return 0.0
    
    base_fine = 25.0
    percentage_fee = contamination_pct * 100.0 * 1.0
    penalty = base_fine + percentage_fee
    
    return float(penalty)

class InputProcessor:
    """Manages the intake and processing of waste submissions."""
    
    def __init__(self):
        self.mapping_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'waste_mapping.json'))
        self.mappings = self._load_mappings()

    def _load_mappings(self):
        if not os.path.exists(self.mapping_file):
            print(f"Error: Required composition mapping file '{self.mapping_file}' not found.")
            return {}
        try:
            with open(self.mapping_file, mode='r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading waste mapping: {e}")
            return {}
            
    def get_allowed_bins(self, zone):
        """Returns allowed bins for a given zone."""
        zone_mappings = self.mappings.get('zone_mappings', {})
        return zone_mappings.get(zone.strip().lower(), [])

    def process_input(self, user_id, category, quantity, items_list):
        """
        Receives user inputs, conducts contamination and penalty metrics,
        and logs the finalized dispatch event.
        """
        if not items_list:
            print("Error: The items list is empty.")
            return None
            
        try:
            quantity = float(quantity)
        except ValueError:
            print("Error: Quantity must be a valid number.")
            return None

        category = category.strip().lower()
        valid_items_dict = self.mappings.get('valid_items', {})
        
        if category not in valid_items_dict:
            print(f"Error: Waste category '{category}' is not recognized in mapping.")
            return None
            
        # Compute metrics
        contamination = calculate_automated_contamination(quantity)
        contamination_pct = contamination / quantity if quantity > 0 else 0.0
        penalty = calculate_penalty(contamination_pct)
        
        input_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        
        event_data = {
            'input_id': input_id,
            'user_id': user_id,
            'category': category.strip(),
            'quantity': quantity,
            'contamination': contamination,
            'penalty': penalty
        }
        
        logger.log_event(event_data)
        return event_data

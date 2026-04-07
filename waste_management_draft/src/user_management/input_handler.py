import json
import os
import datetime
import uuid
import logger

def calculate_contamination(quantity, items_list, valid_items):
    """
    Calculates contamination by checking if the items entered are valid 
    according to the predefined valid_items list from JSON.
    """
    if not items_list:
        return 0.0

    valid_map = {item.lower(): True for item in valid_items}
            
    invalid_count = 0
    for item in items_list:
        item_lower = item.strip().lower()
        if not valid_map.get(item_lower, False):
            invalid_count += 1
            
    # Contamination grows proportionally with the quantity and how many invalid items exist 
    contamination = quantity * invalid_count
    return float(contamination)

def calculate_penalty(contamination, category):
    """
    Calculates the penalty based on contamination level and waste category severity.
    """
    rates = {
        'biodegradable': (1, 2),
        'recyclable': (1, 3),
        'e-waste': (2, 5),
        'hazardous': (3, 6)
    }
    
    category = category.strip().lower()
    severity, base_rate = rates.get(category, (1, 1))
    
    penalty = contamination * severity * base_rate
    return float(penalty)

class InputProcessor:
    """Manages the intake and processing of waste submissions."""
    
    def __init__(self):
        self.mapping_file = os.path.join(os.path.dirname(__file__), 'waste_mapping.json')
        self.mappings = self._load_mappings()

    def _load_mappings(self):
        if not os.path.exists(self.mapping_file):
            print(f"Error: Required composition mapping file '{self.mapping_file}' not found.")
            return {}
        with open(self.mapping_file, mode='r', encoding='utf-8') as f:
            return json.load(f)
            
    def get_allowed_bins(self, zone):
        """Returns allowed bins for a given zone."""
        zone_mappings = self.mappings.get('zone_mappings', {})
        return zone_mappings.get(zone.strip().lower(), [])

    def process_input(self, user_id, category, quantity, items_list):
        """
        Receives user inputs, conducts contamination and penalty metrics,
        and logs the finalized dispatch event.
        """
        # --- 1. Basic Validation ---
        if not items_list:
            print("Error: The items list is empty.")
            return None
            
        try:
            quantity = float(quantity)
        except ValueError:
            print("Error: Quantity must be a valid number.")
            return None

        # --- 2. Load Valid Items ---
        category = category.strip().lower()
        valid_items_dict = self.mappings.get('valid_items', {})
        
        if category not in valid_items_dict:
            print(f"Error: Waste category '{category}' is not recognized in mapping.")
            return None
            
        valid_items = valid_items_dict[category]
                
        # --- 3. Compute Metrics ---
        contamination = calculate_contamination(quantity, items_list, valid_items)
        penalty = calculate_penalty(contamination, category)
        
        # --- 4. Package and Log Result ---
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        input_id = f"EVT-{uuid.uuid4().hex[:8].upper()}"
        
        event_data = {
            'input_id': input_id,
            'user_id': user_id,
            'category': category.strip(),
            'quantity': quantity,
            'contamination': contamination,
            'penalty': penalty,
            'timestamp': timestamp_str
        }
        
        logger.log_event(event_data)
        return event_data

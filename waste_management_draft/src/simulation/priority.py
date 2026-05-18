# src/simulation/priority.py
# Module: Priority Scoring Module
# Rank urgency of bin collection based on weighted factors and emergency bonuses using central constants.

from utils import constants

class PriorityScoring:
    """Calculates collection urgency for each bin using centralized constants."""
    
    def __init__(self):
        self.weight_fill = constants.WEIGHT_FILL
        self.weight_source = constants.WEIGHT_SOURCE
        self.weight_category = constants.WEIGHT_CATEGORY
        self.source_importance = constants.SOURCE_IMPORTANCE
        self.category_urgency = constants.CATEGORY_URGENCY
        self.emergency_bonus = constants.EMERGENCY_BONUS

    def calculate_score(self, bin_obj):
        """Calculates a priority score from 0-100 based on weighted factors."""
        # 1. Fill percentage factor (0-100)
        fill_score = bin_obj.get_fill_percentage()
        
        # 2. Source importance factor (0-100, default 0)
        source_score = self.source_importance.get(bin_obj.source_type, 0)
        
        # 3. Category urgency factor (0-100, default 0)
        category_score = self.category_urgency.get(bin_obj.waste_type, 0)
        
        # Weighted sum
        final_score = (
            (fill_score * self.weight_fill) + 
            (source_score * self.weight_source) + 
            (category_score * self.weight_category)
        )
        
        # Apply immense bonus if in emergency state to bypass normal ordering
        if getattr(bin_obj, 'is_emergency', False):
            final_score += self.emergency_bonus
            
        return round(final_score, 2)

    def rank_bins(self, bins):
        """Returns a list of (bin, score) tuples sorted by urgency (highest first)."""
        ranked_list = []
        for b in bins:
            score = self.calculate_score(b)
            ranked_list.append((b, score))
        
        # Sort by score descending
        ranked_list.sort(key=lambda x: x[1], reverse=True)
        return ranked_list

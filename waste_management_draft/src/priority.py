# src/priority.py
# Module: Priority Scoring Module
# Purpose: Rank urgency of bin collection based on weighted factors.

class PriorityScoring:
    """Calculates collection urgency for each bin."""
    
    # Predefined weights for different factors
    WEIGHT_FILL = 0.50
    WEIGHT_SOURCE = 0.30
    WEIGHT_CATEGORY = 0.20
    
    # Predefined importance factors for source types
    SOURCE_IMPORTANCE = {
        'Hospital': 100,
        'Market': 80,
        'Commercial': 60,
        'Apartment': 40,
        'Household': 20
    }
    
    # Updated to match the 4 waste categories from the project spec
    CATEGORY_URGENCY = {
        'Hazardous': 100,     # Chemicals, medical waste — highest urgency
        'Electronic': 85,     # E-waste needs specialized handling
        'Biodegradable': 70,  # Decomposes quickly, attracts pests
        'Recyclable': 40      # Least urgent, stable materials
    }

    def calculate_score(self, bin_obj):
        """Calculates a priority score from 0-100 based on weighted factors."""
        # 1. Fill percentage factor (0-100)
        fill_score = bin_obj.get_fill_percentage()
        
        # 2. Source importance factor (0-100, default 0)
        source_score = self.SOURCE_IMPORTANCE.get(bin_obj.source_type, 0)
        
        # 3. Category urgency factor (0-100, default 0)
        category_score = self.CATEGORY_URGENCY.get(bin_obj.waste_type, 0)
        
        # Weighted sum
        final_score = (
            (fill_score * self.WEIGHT_FILL) + 
            (source_score * self.WEIGHT_SOURCE) + 
            (category_score * self.WEIGHT_CATEGORY)
        )
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

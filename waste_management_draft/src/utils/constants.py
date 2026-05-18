# src/utils/constants.py
# Standardized global constants for the WasteWise system

# Priority Scoring Weights
WEIGHT_FILL = 0.50
WEIGHT_SOURCE = 0.30
WEIGHT_CATEGORY = 0.20

# Priority Scoring Importance Factors
SOURCE_IMPORTANCE = {
    'Hospital': 100,
    'Market': 80,
    'Commercial': 60,
    'Apartment': 40,
    'Household': 20
}

# Category Urgency Scores
CATEGORY_URGENCY = {
    'Hazardous': 100,
    'Electronic': 85,
    'Biodegradable': 70,
    'Recyclable': 40
}

# Emergency Priority Bonus
EMERGENCY_BONUS = 1000.0

# Facility Emission Limits and Rates
EMISSION_LIMIT = 150.0  # Max CO2 emissions allowed before failover triggers
EMISSION_RATES = {
    'Biodegradable': 0.05,  # kg CO2 per kg waste
    'Recyclable': 0.02,
    'Hazardous': 0.15,
    'Electronic': 0.08
}

# Resident Warning and Contamination Penalty Constants
CONTAMINATION_WARNING_THRESHOLD = 0.10  # Warn if contamination > 10%
PENALTY_RATES = {
    'biodegradable': (1, 2),  # (severity, base_rate)
    'recyclable': (1, 3),
    'e-waste': (2, 5),
    'hazardous': (3, 6)
}

# GUI Colors
DARK_MODE_BG = "#2b2b2b"
LIGHT_MODE_BG = "#f4f4f9"
DARK_MODE_FG = "#ffffff"
LIGHT_MODE_FG = "#000000"
DARK_MODE_INPUT = "#3c3f41"
LIGHT_MODE_INPUT = "#ffffff"

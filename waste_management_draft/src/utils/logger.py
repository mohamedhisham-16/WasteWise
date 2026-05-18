# src/utils/logger.py
# Centralized logging module for all system event logs in WasteWise

import os
from datetime import datetime
from utils import csv_utils

# Base paths resolved dynamically relative to this file
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

DISPOSAL_LOG = os.path.join(DATA_DIR, "disposal_events.csv")
EMERGENCY_LOG = os.path.join(DATA_DIR, "emergency_logs.csv")
ROUTE_LOG = os.path.join(DATA_DIR, "route_logs.csv")
FACILITY_LOG = os.path.join(DATA_DIR, "facility_logs.csv")

def get_current_timestamp():
    """Returns standard unified timestamp formatting."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(event_data):
    """
    Logs general waste disposal events from residents.
    """
    headers = ["input_id", "user_id", "category", "quantity", "contamination", "penalty", "timestamp"]
    if "timestamp" not in event_data:
        event_data["timestamp"] = get_current_timestamp()
    csv_utils.append_csv(DISPOSAL_LOG, event_data, headers=headers)

def log_emergency(bin_id, reason, status, vehicle_assigned="None"):
    """
    Logs emergency state changes (ACTIVE, CLOSED).
    """
    headers = ["timestamp", "bin_id", "reason", "vehicle_assigned", "status"]
    row = {
        "timestamp": get_current_timestamp(),
        "bin_id": bin_id,
        "reason": reason,
        "vehicle_assigned": vehicle_assigned,
        "status": status
    }
    csv_utils.append_csv(EMERGENCY_LOG, row, headers=headers)

def log_route_event(vehicle_id, route_str, distance_km, bins_collected, waste_collected_kg):
    """
    Logs collection route completion details.
    """
    headers = ["timestamp", "vehicle_id", "route", "distance_km", "bins_collected", "waste_collected_kg"]
    row = {
        "timestamp": get_current_timestamp(),
        "vehicle_id": vehicle_id,
        "route": route_str,
        "distance_km": f"{distance_km:.2f}",
        "bins_collected": bins_collected,
        "waste_collected_kg": f"{waste_collected_kg:.2f}"
    }
    csv_utils.append_csv(ROUTE_LOG, row, headers=headers)

def log_facility_event(facility_id, event_type, details, redirected_to="None"):
    """
    Logs facility specific occurrences such as high emissions and failovers.
    """
    headers = ["timestamp", "facility_id", "event_type", "details", "redirected_to"]
    row = {
        "timestamp": get_current_timestamp(),
        "facility_id": facility_id,
        "event_type": event_type,
        "details": details,
        "redirected_to": redirected_to
    }
    csv_utils.append_csv(FACILITY_LOG, row, headers=headers)

def reset_all_logs():
    """
    Clears all transient operational/simulation CSV log files by writing empty data with headers.
    """
    # 1. Disposal Events
    csv_utils.write_csv(
        DISPOSAL_LOG, 
        [], 
        headers=["input_id", "user_id", "category", "quantity", "contamination", "penalty", "timestamp"]
    )
    
    # 2. Emergency Logs
    csv_utils.write_csv(
        EMERGENCY_LOG, 
        [], 
        headers=["timestamp", "bin_id", "reason", "vehicle_assigned", "status"]
    )
    
    # 3. Route Logs
    csv_utils.write_csv(
        ROUTE_LOG, 
        [], 
        headers=["timestamp", "vehicle_id", "route", "distance_km", "bins_collected", "waste_collected_kg"]
    )
    
    # 4. Facility Logs
    csv_utils.write_csv(
        FACILITY_LOG, 
        [], 
        headers=["timestamp", "facility_id", "event_type", "details", "redirected_to"]
    )
    
    print("[SYSTEM] All persistent logs reset successfully.")

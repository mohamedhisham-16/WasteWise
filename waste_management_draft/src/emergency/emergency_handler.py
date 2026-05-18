# src/emergency/emergency_handler.py
# Module: Emergency Waste Handling Subsystem
# Purpose: Automatically detects critical waste threats, creates emergency incidents, 
#          handles persistent CSV event logs, and resolves emergency cases upon successful pickup.

import os
import csv
from datetime import datetime

# Persistent CSV database path for emergency logs
LOGS_FILE = r"c:\NarenClg\Sem 2\Python\Project\WasteWise\waste_management_draft\src\data\emergency_logs.csv"

def check_emergency_conditions(bin_obj):
    """
    Checks the status metrics of a bin against municipal emergency rules.
    If conditions are met, marks the bin as an active emergency.
    """
    if getattr(bin_obj, 'is_emergency', False):
        return  # Already flagged as an active emergency

    reason = None
    fill_pct = bin_obj.get_fill_percentage()

    # 1. Hazardous waste fill level above 90%
    if bin_obj.waste_type == 'Hazardous' and fill_pct >= 90.0:
        reason = "Hazardous Waste Overflow Threat"
    
    # 2. Hospital hazardous bins above 80%
    elif bin_obj.waste_type == 'Hazardous' and bin_obj.source_type == 'Hospital' and fill_pct >= 80.0:
        reason = "Critical Hospital Hazardous Waste Load"
    
    # 3. Contamination level above threshold (20% contamination mixed in)
    elif bin_obj.contamination_level >= 0.20:
        reason = f"Critical Contamination Detected ({bin_obj.contamination_level*100:.1f}%)"
    
    # 4. Electronic waste overflow (fill level equals or exceeds maximum capacity)
    elif bin_obj.waste_type == 'Electronic' and fill_pct >= 100.0:
        reason = "Electronic Waste Overflow"
    
    # 5. Multiple failed collection attempts (3 or more attempts with no vehicle assigned)
    elif getattr(bin_obj, 'failed_collection_attempts', 0) >= 3:
        reason = f"Multiple Collection Failures ({bin_obj.failed_collection_attempts} attempts)"

    if reason:
        trigger_emergency(bin_obj, reason)

def trigger_emergency(bin_obj, reason):
    """Marks a bin as active emergency and creates a CSV log entry."""
    bin_obj.is_emergency = True
    bin_obj.emergency_reason = reason
    bin_obj.emergency_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    log_emergency_event(bin_obj.bin_id, reason, "ACTIVE")
    print(f"[EMERGENCY TRIGGERED] Bin {bin_obj.bin_id}: {reason}")

def log_emergency_event(bin_id, reason, status, vehicle_assigned="None"):
    """Saves structured emergency logs in a persistent database CSV."""
    os.makedirs(os.path.dirname(LOGS_FILE), exist_ok=True)
    file_exists = os.path.exists(LOGS_FILE)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(LOGS_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "bin_id", "reason", "vehicle_assigned", "status"])
        writer.writerow([timestamp, bin_id, reason, vehicle_assigned, status])

def resolve_emergency(bin_obj, vehicle_id):
    """Closes an emergency, updates CSV logs, and resets bin parameters."""
    if getattr(bin_obj, 'is_emergency', False):
        log_emergency_event(bin_obj.bin_id, "Resolved", "CLOSED", vehicle_assigned=vehicle_id)
        
        bin_obj.is_emergency = False
        bin_obj.emergency_reason = None
        bin_obj.emergency_timestamp = None
        bin_obj.failed_collection_attempts = 0
        print(f"[EMERGENCY RESOLVED] Bin {bin_obj.bin_id} collection complete by Vehicle {vehicle_id}.")

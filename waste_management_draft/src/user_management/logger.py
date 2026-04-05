import csv
import os

# File to store all disposal events
LOG_FILE = os.path.join("logs", "disposal_events.csv")
HEADERS = ["input_id", "user_id", "category", "quantity", "contamination", "penalty", "timestamp"]

def _ensure_dir():
    """Ensure the logs directory exists before creating the file."""
    log_dir = os.path.dirname(LOG_FILE)
    # Checking if log_dir is non-empty just in case LOG_FILE is just a filename
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

def log_event(event_data):
    """
    Records a waste disposal event into the CSV.
    Creates file and headers if missing.
    """
    _ensure_dir()
    file_exists = os.path.isfile(LOG_FILE)
    
    # Open in 'a' mode for append to avoid overwriting existing events
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        
        # Write headers if it's a new file
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(event_data)

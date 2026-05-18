import csv
import os

# Use absolute path relative to this file to ensure it's found when imported from other directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "users.csv")
HEADERS = ["user_id", "name", "role", "zone"]

def initialize_csv():
    """Create the CSV file with headers if it does not exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(HEADERS)

def load_users_from_csv():
    """Read all users from the CSV and return a list of dictionaries."""
    initialize_csv()
    users_data = []
    with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users_data.append(row)
    return users_data

def save_all_users_to_csv(users_data):
    """Overwrite the CSV with a fresh list of user dictionaries.
    Used when deleting a user to update the entire file."""
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(users_data)

def append_user_to_csv(user_data):
    """Append a single user dictionary to the CSV file.
    Used for efficiently adding a new user without rewriting the whole file."""
    initialize_csv()
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writerow(user_data)

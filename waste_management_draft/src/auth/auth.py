# src/auth/auth.py
# Handles user authentication and logging login history using central utilities

import os
from datetime import datetime
from auth.user import User
from utils import csv_utils

USERS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "users.csv"))
HISTORY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "login_history.csv"))

def load_users():
    """Reads all users from users.csv and returns a list of User objects."""
    data = csv_utils.read_csv(USERS_FILE, as_dict=True)
    return [User.from_dict(row) for row in data]

def login(user_id, password):
    """
    Verifies:
    - user exists
    - password matches
    Returns:
    - User object if valid
    - None if invalid
    """
    users = load_users()
    for user in users:
        if user.user_id == user_id:
            if user.password == password:
                record_login_attempt(user_id, True)
                return user
            else:
                record_login_attempt(user_id, False)
                return None
    
    # User not found
    record_login_attempt(user_id, False)
    return None

def record_login_attempt(user_id, success):
    """
    Saves login history into login_history.csv
    Columns: timestamp,user_id,status
    """
    headers = ["timestamp", "user_id", "status"]
    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "user_id": user_id,
        "status": "SUCCESS" if success else "FAILED"
    }
    csv_utils.append_csv(HISTORY_FILE, row, headers=headers, as_dict=True)

import os
import csv
from datetime import datetime
from user_management import csv_handler
from user_management.user import User

def load_users():
    """Reads all users from users.csv and returns a list of User objects."""
    data = csv_handler.load_users_from_csv()
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
    base_dir = os.path.dirname(os.path.abspath(csv_handler.__file__))
    log_file = os.path.join(base_dir, "login_history.csv")
    
    file_exists = os.path.exists(log_file)
    with open(log_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "user_id", "status"])
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        status = "SUCCESS" if success else "FAILED"
        writer.writerow([timestamp, user_id, status])

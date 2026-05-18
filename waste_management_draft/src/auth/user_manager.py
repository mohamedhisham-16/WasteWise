# src/auth/user_manager.py
# Manages user accounts, loading/saving from users.csv using common CSV utilities

import os
from auth.user import User
from utils import csv_utils

CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "users.csv"))
HEADERS = ["user_id", "name", "password", "role", "zone", "violation_score"]

class UserManager:
    def __init__(self):
        self.users = []
        self._load_users()

    def _load_users(self):
        """Populates the users list from the CSV file."""
        data = csv_utils.read_csv(CSV_FILE, as_dict=True)
        self.users = [User.from_dict(row) for row in data]

    def add_user(self, user_id, name, role, zone, password=None, violation_score=0):
        """Adds a new user if the user_id is unique."""
        if self.search_user(user_id) is not None:
            print(f"Error: User with ID '{user_id}' already exists.")
            return False
            
        if password is None:
            password = user_id + "123"

        new_user = User(user_id, name, password, role, zone, violation_score)
        self.users.append(new_user)
        
        # Append only the new user directly to the CSV
        csv_utils.append_csv(CSV_FILE, new_user.to_dict(), headers=HEADERS, as_dict=True)
        return True

    def view_users(self):
        """Prints all users in a formatted table."""
        if not self.users:
            print("No users found.")
            return

        print("-" * 65)
        print(f"{'User ID':<10} | {'Name':<20} | {'Role':<10} | {'Zone'}")
        print("-" * 65)
        for user in self.users:
            print(f"{user.user_id:<10} | {user.name:<20} | {user.role:<10} | {user.zone}")
        print("-" * 65)

    def search_user(self, user_id):
        """Retrieves a User object by user_id, or None if not found."""
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def delete_user(self, user_id):
        """Deletes a user by user_id and updates the CSV file."""
        user = self.search_user(user_id)
        if user is None:
            print(f"Error: User with ID '{user_id}' not found.")
            return False

        self.users.remove(user)
        # We must overwrite the entire file when an item is removed
        users_data = [u.to_dict() for u in self.users]
        csv_utils.write_csv(CSV_FILE, users_data, headers=HEADERS, as_dict=True)
        return True

    def update_user(self, user_id, name, role, zone, password, violation_score):
        """Updates an existing user's details and rewrites the CSV file."""
        user = self.search_user(user_id)
        if user is None:
            print(f"Error: User with ID '{user_id}' not found.")
            return False
            
        user.name = name
        user.role = role
        user.zone = zone
        user.password = password
        user.violation_score = int(violation_score)
        
        # Overwrite the CSV
        users_data = [u.to_dict() for u in self.users]
        csv_utils.write_csv(CSV_FILE, users_data, headers=HEADERS, as_dict=True)
        return True


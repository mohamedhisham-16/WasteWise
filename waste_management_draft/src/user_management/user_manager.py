from user_management.user import User
from user_management import csv_handler

class UserManager:
    def __init__(self):
        # Cache of user objects in memory for fast lookup
        self.users = []
        self._load_users()

    def _load_users(self):
        """Internal method to populate the users list from the CSV file."""
        data = csv_handler.load_users_from_csv()
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
        
        # Append only the new user directly to the CSV to avoid rewriting everything
        csv_handler.append_user_to_csv(new_user.to_dict())
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
        csv_handler.save_all_users_to_csv(users_data)
        return True

import sys
from user_manager import UserManager
from input_handler import InputProcessor

def admin_menu(manager):
    """Admin specific functions for managing users."""
    while True:
        print("\n" + "="*40)
        print("          Admin Dashboard          ")
        print("="*40)
        print("1. Add User")
        print("2. View Users")
        print("3. Search User")
        print("4. Delete User")
        print("5. Logout")
        print("="*40)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\n--- Add New User ---")
            user_id = input("Enter User ID: ").strip()
            name = input("Enter Name: ").strip()
            role = input("Enter Role (Resident/Driver/Admin/Facility): ").strip()
            zone = input("Enter Zone (residential/medical/factory): ").strip()
            
            if not user_id or not name or not role:
                print("Error: User ID, Name, and Role are mandatory!")
                continue
                
            success = manager.add_user(user_id, name, role, zone)
            if success:
                print(f"Success: User '{name}' added successfully.")
                
        elif choice == '2':
            print("\n--- All Registered Users ---")
            manager.view_users()
            
        elif choice == '3':
            print("\n--- Search User ---")
            user_id = input("Enter User ID to search: ").strip()
            if not user_id:
                print("Error: User ID cannot be empty.")
                continue
                
            user = manager.search_user(user_id)
            if user:
                print(f"\nUser Found!")
                print("-" * 30)
                print(f"User ID  : {user.user_id}")
                print(f"Name     : {user.name}")
                print(f"Role     : {user.role}")
                print(f"Zone     : {user.zone}")
                print("-" * 30)
            else:
                print(f"Error: User with ID '{user_id}' not found.")
                
        elif choice == '4':
            print("\n--- Delete User ---")
            user_id = input("Enter User ID to delete: ").strip()
            if not user_id:
                print("Error: User ID cannot be empty.")
                continue
                
            success = manager.delete_user(user_id)
            if success:
                print(f"Success: User with ID '{user_id}' deleted successfully.")
                
        elif choice == '5':
            print("\nLogging out... Returning to login screen.")
            break
            
        else:
            print("Invalid choice! Please enter a number between 1 and 5.")

def resident_menu(manager, user):
    """Resident specific functions."""
    while True:
        print("\n" + "="*40)
        print(f"         Resident Home: {user.name}         ")
        print("="*40)
        print("1. Dump Waste (Placeholder)")
        print("2. View Own Details")
        print("3. Logout")
        print("="*40)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n--- Dump Waste ---")
            processor = InputProcessor()
            allowed_bins = processor.get_allowed_bins(user.zone)
            
            if not allowed_bins:
                print(f"Error: No bins configured for your zone ('{user.zone}').")
                continue
                
            print(f"Available bins for your zone ({user.zone}):")
            for idx, bin_name in enumerate(allowed_bins, 1):
                print(f"{idx}. {bin_name.capitalize()}")
                
            bin_choice = input("Select a bin by number: ").strip()
            try:
                bin_idx = int(bin_choice) - 1
                if bin_idx < 0 or bin_idx >= len(allowed_bins):
                    raise ValueError
                selected_bin = allowed_bins[bin_idx]
            except ValueError:
                print("Error: Invalid bin selection.")
                continue
                
            items_input = input("Enter items you are dumping (comma separated): ").strip()
            items_list = [item.strip() for item in items_input.split(',')] if items_input else []
            
            quantity = input("Enter estimated quantity (e.g. in units/kg): ").strip()
            
            print(f"\nProcessing deposit into {selected_bin.capitalize()} bin...")
            result = processor.process_input(user.user_id, selected_bin, quantity, items_list)
            
            if result is not None:
                print("Deposit successful!")
                print(f"Logged Event ID: {result['input_id']}")
                if result['contamination'] > 0:
                    print(f"Warning: Contamination detected! Level: {result['contamination']}, Penalty: {result['penalty']}")
            else:
                print("Deposit failed due to errors.")
            
        elif choice == '2':
            print("\n--- Profile Details ---")
            print("-" * 30)
            print(f"User ID  : {user.user_id}")
            print(f"Name     : {user.name}")
            print(f"Role     : {user.role}")
            print(f"Zone     : {user.zone}")
            print("-" * 30)
            
        elif choice == '3':
            print("\nLogging out... Returning to login screen.")
            break
            
        else:
            print("Invalid choice! Please enter a number between 1 and 3.")

def driver_menu(manager, user):
    """Driver specific functions."""
    while True:
        print("\n" + "="*40)
        print(f"         Driver Dashboard: {user.name}         ")
        print("="*40)
        print("1. View Assigned Tasks (Placeholder)")
        print("2. Mark Collection Done (Placeholder)")
        print("3. Logout")
        print("="*40)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n--- Assigned Tasks ---")
            print("Feature coming soon! (Task retrieval will happen here)")
            
        elif choice == '2':
            print("\n--- Mark Collection Done ---")
            print("Feature coming soon! (Updating task status here)")
            
        elif choice == '3':
            print("\nLogging out... Returning to login screen.")
            break
            
        else:
            print("Invalid choice! Please enter a number between 1 and 3.")

def login_screen(manager):
    """Handles the login process and redirects based on roles."""
    while True:
        print("\n" + "*"*40)
        print("    Welcome to WasteWise System    ")
        print("*"*40)
        print("Type 'exit' to quit the application.")
        
        user_id = input("Enter your User ID to login: ").strip()
        
        if user_id.lower() == 'exit':
            print("\nSaving data... Exiting WasteWise System. Goodbye!")
            sys.exit(0)
            
        # Prevent inputting empty string
        if not user_id:
            print("Error: User ID cannot be empty. Please try again.")
            continue
            
        # Use existing manager to validate login credentials
        user = manager.search_user(user_id)
        
        if user is None:
            print(f"Error: User with ID '{user_id}' not found. Please try again.")
        else:
            print(f"\nLogin Successful! Welcome back, {user.name}.")
            
            # Convert user role to lowercase to handle casing mismatches (e.g. "Admin" vs "admin")
            role = user.role.strip().lower()
            
            # Route to the appropriate menu loop
            if role == "admin":
                admin_menu(manager)
            elif role == "resident":
                resident_menu(manager, user)
            elif role == "driver":
                driver_menu(manager, user)
            else:
                # Basic fallback if they enter a role not managed by these menus
                print(f"\nNotice: Menu options for the role '{user.role}' are not available yet.")
                print("Logging out...")

def main():
    manager = UserManager()
    login_screen(manager)

if __name__ == "__main__":
    main()

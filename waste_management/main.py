import sys
from bin_manager import BinManager
from vehicle_manager import VehicleManager
from facility_manager import FacilityManager

def display_menu():
    print("\n--- WasteWise Management System ---")
    print("1. Manage Bins")
    print("2. Manage Vehicles")
    print("3. Manage Facilities")
    print("4. Exit")
    return input("Select an option (1-4): ")

def manage_bins(bin_mgr):
    print("\n--- Bin Management ---")
    print("1. List all Bins")
    print("2. Add a new Bin")
    choice = input("Select an option: ")
    
    if choice == '1':
        bins = bin_mgr.list_bins()
        print("\nCurrent Bins:")
        for b in bins:
            print(b)
    elif choice == '2':
        bin_id = input("Enter Bin ID: ")
        location = input("Enter Location: ")
        bin_mgr.add_bin({"id": bin_id, "location": location})
        print(f"Bin {bin_id} added successfully.")

def manage_vehicles(vehicle_mgr):
    print("\n--- Vehicle Management ---")
    print("1. List all Vehicles")
    print("2. Add a new Vehicle")
    choice = input("Select an option: ")
    
    if choice == '1':
        vehicles = vehicle_mgr.list_vehicles()
        print("\nCurrent Vehicles:")
        for v in vehicles:
            print(v)
    elif choice == '2':
        v_id = input("Enter Vehicle ID: ")
        vehicle_mgr.add_vehicle({"id": v_id})
        print(f"Vehicle {v_id} added successfully.")

def manage_facilities(facility_mgr):
    print("\n--- Facility Management ---")
    print("1. List all Facilities")
    print("2. Add a new Facility")
    choice = input("Select an option: ")
    
    if choice == '1':
        facilities = facility_mgr.list_facilities()
        print("\nCurrent Facilities:")
        for f in facilities:
            print(f)
    elif choice == '2':
        f_id = input("Enter Facility ID: ")
        facility_mgr.add_facility({"id": f_id})
        print(f"Facility {f_id} added successfully.")

def main():
    # Initialize the managers
    bin_mgr = BinManager()
    vehicle_mgr = VehicleManager()
    facility_mgr = FacilityManager()
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            manage_bins(bin_mgr)
        elif choice == '2':
            manage_vehicles(vehicle_mgr)
        elif choice == '3':
            manage_facilities(facility_mgr)
        elif choice == '4':
            print("Exiting WasteWise. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()

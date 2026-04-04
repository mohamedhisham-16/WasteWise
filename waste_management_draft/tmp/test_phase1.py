# /tmp/test_phase1.py
# Verification script for Phase 1 Models and Graph

import sys
import os
sys.path.append(os.path.abspath('src'))

from models import Bin, Vehicle, Facility
from distance_graph import DistanceGraph

def test_models():
    print("Testing Models...")
    # 1. Test Bin
    test_bin = Bin("B001", 100.0, "Organic", "Hospital", "Node_A")
    test_bin.fill_level = 95.0
    print(f"  Bin Fill Percentage: {test_bin.get_fill_percentage()}% (Expected: 95.0%)")
    
    # 2. Test Vehicle Compatibility
    test_vehicle = Vehicle("V001", "Compactor", 500.0, ["Organic", "Recyclable"], "Depot_1")
    print(f"  Can Vehicle V001 collect Bin B001? {test_vehicle.can_collect(test_bin)} (Expected: True)")
    
    # 3. Test Facility Capacity
    test_facility = Facility("F001", "Compost Unit", 1000.0, ["Organic"], 10.0, "Node_F")
    print(f"  Can Facility F001 process Organic waste? {test_facility.can_process(test_vehicle.supported_waste_types[0], test_vehicle.current_load)} (Expected: True)")
    print(f"  Facility F001 currently has load: {test_facility.current_load}")

def test_graph():
    print("\nTesting Distance Graph...")
    graph = DistanceGraph()
    graph.add_edge("Home", "Office", 5)  # 5 km
    graph.add_edge("Office", "Gym", 2)   # 2 km
    
    dist_home_office = graph.get_distance("Home", "Office")
    dist_gym_office = graph.get_distance("Gym", "Office")
    dist_home_gym = graph.get_distance("Home", "Gym")
    
    print(f"  Distance Home -> Office: {dist_home_office} km (Expected: 5)")
    print(f"  Distance Gym -> Office: {dist_gym_office} km (Expected: 2)")
    print(f"  Distance Home -> Gym: {dist_home_gym} km (Expected: inf)")
    
    print(f"  Office Neighbors: {list(graph.get_neighbors('Office').keys())} (Expected: ['Home', 'Gym'])")

if __name__ == "__main__":
    try:
        test_models()
        print("\nPhase 1 Verification SUCCESSFUL!")
    except Exception as e:
        print(f"\nVerification FAILED: {str(e)}")

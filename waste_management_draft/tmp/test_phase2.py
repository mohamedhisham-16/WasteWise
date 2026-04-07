# tmp/test_phase2.py
# Verification script for Phase 2: Core Operational Modules
# Tests the full cycle: Load Data -> Fill Bins -> Prioritize -> Collect -> Unload

import sys
import os
sys.path.append(os.path.abspath('src'))

from data_loader import load_all
from engine import SimulationEngine

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_full_cycle():
    # --- Setup ---
    separator("SETUP: Loading Sample Data")
    bins, vehicles, facilities, graph = load_all()
    engine = SimulationEngine(bins, vehicles, facilities, graph)
    print(f"  Loaded {len(bins)} bins, {len(vehicles)} vehicles, "
          f"{len(facilities)} facilities, {len(graph.nodes)} graph nodes.")

    # --- Test 1: Dijkstra Shortest Path ---
    separator("TEST 1: Dijkstra's Shortest Path")
    path, cost = graph.shortest_path("Depot_1", "Node_F3")
    print(f"  Depot_1 -> Node_F3: Path = {path}, Cost = {cost}")
    assert cost < float('inf'), "FAIL: No path found from Depot_1 to Node_F3"
    print("  PASSED [OK]")

    path2, cost2 = graph.shortest_path("Depot_2", "Node_H1")
    print(f"  Depot_2 -> Node_H1: Path = {path2}, Cost = {cost2}")
    assert cost2 < float('inf'), "FAIL: No path found from Depot_2 to Node_H1"
    print("  PASSED [OK]")

    # --- Test 2: Fill Bins to Trigger Alerts ---
    separator("TEST 2: Filling Bins")
    # Fill a hospital hazardous bin to 95%
    engine.add_waste("B004", "Hazardous", 57.0, user_id="User_001")
    # Fill a commercial recyclable bin to 90%
    engine.add_waste("B006", "Recyclable", 108.0, user_id="User_002")
    # Fill a residential biodegradable bin to 85%
    engine.add_waste("B001", "Biodegradable", 85.0, user_id="User_003")
    # Low fill — should NOT trigger
    engine.add_waste("B010", "Electronic", 10.0, user_id="User_004")

    # --- Test 3: Run Optimization ---
    separator("TEST 3: Running Optimization Cycle")
    summary = engine.run_optimization(alert_threshold=80.0)

    print(f"\n  --- SUMMARY ---")
    print(f"  Bins detected:    {summary['bins_detected']}")
    print(f"  Bins collected:   {summary['bins_collected']}")
    print(f"  Vehicles sent:    {summary['vehicles_dispatched']}")
    print(f"  Vehicles unloaded:{summary['vehicles_unloaded']}")
    print(f"  Failed:           {summary['failed_allocations']}")

    assert summary["bins_detected"] >= 3, f"FAIL: Expected >=3 bins detected, got {summary['bins_detected']}"
    assert summary["bins_collected"] >= 3, f"FAIL: Expected >=3 bins collected, got {summary['bins_collected']}"
    print("  PASSED [OK]")

    # --- Test 4: Verify Post-Collection State ---
    separator("TEST 4: Post-Collection Verification")
    b004 = engine.monitor.find_bin("B004")
    print(f"  Bin B004 fill after collection: {b004.get_fill_percentage():.1f}% (Expected: 0%)")
    assert b004.get_fill_percentage() == 0.0, "FAIL: Bin B004 not cleared after collection"
    print("  PASSED [OK]")

    # --- Test 5: Reset and Verify ---
    separator("TEST 5: System Reset")
    engine.reset_all()
    b001 = engine.monitor.find_bin("B001")
    print(f"  Bin B001 fill after reset: {b001.get_fill_percentage():.1f}% (Expected: 0%)")
    assert b001.get_fill_percentage() == 0.0, "FAIL: Bin B001 not reset"
    v001 = [v for v in vehicles if v.vehicle_id == "V001"][0]
    print(f"  Vehicle V001 location after reset: {v001.location_id} (Expected: Depot_1)")
    assert v001.location_id == "Depot_1", "FAIL: Vehicle V001 not back at depot"
    print("  PASSED [OK]")

    separator("ALL PHASE 2 TESTS PASSED!")


if __name__ == "__main__":
    try:
        test_full_cycle()
    except AssertionError as e:
        print(f"\n  TEST FAILED: {e}")
    except Exception as e:
        print(f"\n  UNEXPECTED ERROR: {type(e).__name__}: {e}")

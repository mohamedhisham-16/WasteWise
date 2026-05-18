# test_facility_failover.py
# Comprehensive test suite for the dual-facility redundancy and failover system.
# Tests: partner lookup, waste rerouting, vehicle allocation failover, edge cases.

import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from simulation.data_loader import load_all, create_sample_facilities, create_city_graph
from simulation.engine import SimulationEngine
from facilities.facility_allocation import FacilityAllocator
from models.models import Facility, Vehicle
from utils import logger

# ─── Helpers ───────────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0

def check(test_name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ PASS: {test_name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {test_name} — {detail}")

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

# ─── Reset logger to avoid file conflicts ──────────────────────────────────────
logger.reset_all_logs()

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 1: Verify Facility Setup (8 facilities, 2 per type)
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 1: Facility Setup Verification")

facilities = create_sample_facilities()
check("Total facility count is 8", len(facilities) == 8, f"Got {len(facilities)}")

# Count by type
from collections import Counter
type_counts = Counter(f.facility_type for f in facilities)
check("2 Compost Units",      type_counts["Compost Unit"] == 2,      f"Got {type_counts.get('Compost Unit', 0)}")
check("2 Recycling Plants",   type_counts["Recycling Plant"] == 2,   f"Got {type_counts.get('Recycling Plant', 0)}")
check("2 Hazmat Processors",  type_counts["Hazmat Processor"] == 2,  f"Got {type_counts.get('Hazmat Processor', 0)}")
check("2 E-Waste Recyclers",  type_counts["E-Waste Recycler"] == 2,  f"Got {type_counts.get('E-Waste Recycler', 0)}")

# Verify IDs
fids = [f.facility_id for f in facilities]
for expected_id in ["F001","F002","F003","F004","F005","F006","F007","F008"]:
    check(f"Facility {expected_id} exists", expected_id in fids, f"Missing {expected_id}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 2: Partner Facility Lookup
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 2: Partner Facility Lookup")

allocator = FacilityAllocator(facilities)

# F001 (Compost) partner should be F005 (Compost)
f001 = next(f for f in facilities if f.facility_id == "F001")
f005 = next(f for f in facilities if f.facility_id == "F005")
partner = allocator.get_partner_facility(f001)
check("F001 partner is F005", partner is not None and partner.facility_id == "F005",
      f"Got {partner.facility_id if partner else 'None'}")

# F005 partner should be F001
partner = allocator.get_partner_facility(f005)
check("F005 partner is F001", partner is not None and partner.facility_id == "F001",
      f"Got {partner.facility_id if partner else 'None'}")

# F002 (Recycling) partner should be F006
f002 = next(f for f in facilities if f.facility_id == "F002")
partner = allocator.get_partner_facility(f002)
check("F002 partner is F006", partner is not None and partner.facility_id == "F006",
      f"Got {partner.facility_id if partner else 'None'}")

# F003 (Hazmat) partner should be F007
f003 = next(f for f in facilities if f.facility_id == "F003")
partner = allocator.get_partner_facility(f003)
check("F003 partner is F007", partner is not None and partner.facility_id == "F007",
      f"Got {partner.facility_id if partner else 'None'}")

# F004 (E-Waste) partner should be F008
f004 = next(f for f in facilities if f.facility_id == "F004")
partner = allocator.get_partner_facility(f004)
check("F004 partner is F008", partner is not None and partner.facility_id == "F008",
      f"Got {partner.facility_id if partner else 'None'}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 3: Partner Lookup When Partner is Inactive
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 3: Partner Lookup When Partner is Inactive")

# Shut down F005, then F001's partner should be None (only 2 compost facilities)
f005.is_active = False
partner = allocator.get_partner_facility(f001)
check("F001 has no active partner when F005 is inactive", partner is None,
      f"Got {partner.facility_id if partner else 'None'}")

# Restore
f005.is_active = True

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 4: Waste Rerouting on Manual Shutdown
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 4: Waste Rerouting on Manual Shutdown")

# Load F001 with 200kg, then shut it down → waste should transfer to F005
for f in facilities: f.reset()  # Clean slate

f001.current_load = 200.0
f001.is_active = False

partner = allocator.reroute_waste_on_shutdown(f001)
check("Reroute returned partner F005", partner is not None and partner.facility_id == "F005",
      f"Got {partner.facility_id if partner else 'None'}")
check("F001 load is now 0 after reroute", f001.current_load == 0.0, f"Got {f001.current_load}")
check("F005 received 200kg", f005.current_load == 200.0, f"Got {f005.current_load}")
check("F001 redirected_count incremented", f001.redirected_count == 1, f"Got {f001.redirected_count}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 5: Reroute When Partner Has Limited Capacity
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 5: Reroute With Partner at Near-Capacity")

for f in facilities: f.reset()

# F005 max capacity is 800. Fill it to 700, then try to reroute 300 from F001
f005.current_load = 700.0
f001.current_load = 300.0
f001.is_active = False

partner = allocator.reroute_waste_on_shutdown(f001)
check("Partial reroute: partner is F005", partner is not None and partner.facility_id == "F005",
      f"Got {partner.facility_id if partner else 'None'}")
check("F005 filled to capacity (800)", f005.current_load == 800.0, f"Got {f005.current_load}")
check("F001 has 200kg stranded (300-100 transferred)", f001.current_load == 200.0, f"Got {f001.current_load}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 6: Reroute When No Partner Available (Both Down)
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 6: EDGE CASE — Both Facilities of Same Type Down")

for f in facilities: f.reset()

f001.current_load = 150.0
f001.is_active = False
f005.is_active = False  # Both compost units down!

partner = allocator.reroute_waste_on_shutdown(f001)
check("No partner available when both are down", partner is None, 
      f"Got {partner.facility_id if partner else 'None'}")
check("F001 load unchanged (stranded)", f001.current_load == 150.0, f"Got {f001.current_load}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 7: Reroute When Facility Has Zero Load
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 7: EDGE CASE — Reroute on Shutdown with Zero Load")

for f in facilities: f.reset()

f001.is_active = False
f001.current_load = 0.0

partner = allocator.reroute_waste_on_shutdown(f001)
check("No reroute needed for empty facility", partner is None, 
      f"Got {partner.facility_id if partner else 'None'}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 8: Vehicle Allocation Failover
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 8: Vehicle Allocation Failover (Primary → Backup)")

bins, vehicles, facilities, graph = load_all()
for f in facilities: f.reset()
allocator = FacilityAllocator(facilities)

# Create a vehicle loaded with Biodegradable waste near Compost Center
v = vehicles[0]  # V001
v.current_load = 100.0
v.collected_waste_type = "Biodegradable"
v.location_id = "Compost Center"  # Closest to F001

# Normal allocation → should pick F001 (closest active compost)
facility = allocator.allocate_facility(v, graph)
check("Normal: allocates to closest compost (F001)", 
      facility is not None and facility.facility_id == "F001",
      f"Got {facility.facility_id if facility else 'None'}")

# Shut down F001 → should failover to F005
f001 = next(f for f in facilities if f.facility_id == "F001")
f001.is_active = False

facility = allocator.allocate_facility(v, graph)
check("Failover: allocates to backup compost (F005)", 
      facility is not None and facility.facility_id == "F005",
      f"Got {facility.facility_id if facility else 'None'}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 9: Vehicle Allocation When Both Facilities Down
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 9: EDGE CASE — Vehicle Allocation When Both Facilities Down")

f005 = next(f for f in facilities if f.facility_id == "F005")
f005.is_active = False  # Both compost facilities now down

facility = allocator.allocate_facility(v, graph)
check("No facility available when both compost down", facility is None,
      f"Got {facility.facility_id if facility else 'None'}")

# Restore
f001.is_active = True
f005.is_active = True

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 10: Vehicle Allocation for Each Waste Type
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 10: Vehicle Allocation Per Waste Type With Failover")

for f in facilities: f.reset()

test_cases = [
    ("Recyclable",    "Recycling Hub",   "F002", "F006"),
    ("Hazardous",     "Hazmat Disposal", "F003", "F007"),
    ("Electronic",    "E-Waste Hub",     "F004", "F008"),
]

for waste_type, location, primary_id, backup_id in test_cases:
    v.current_load = 50.0
    v.collected_waste_type = waste_type
    v.location_id = location
    
    # Normal → primary
    facility = allocator.allocate_facility(v, graph)
    check(f"{waste_type}: normal → {primary_id}", 
          facility is not None and facility.facility_id == primary_id,
          f"Got {facility.facility_id if facility else 'None'}")
    
    # Shutdown primary → backup
    primary = next(f for f in facilities if f.facility_id == primary_id)
    primary.is_active = False
    
    facility = allocator.allocate_facility(v, graph)
    check(f"{waste_type}: failover → {backup_id}", 
          facility is not None and facility.facility_id == backup_id,
          f"Got {facility.facility_id if facility else 'None'}")
    
    primary.is_active = True  # Restore

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 11: Emissions-Triggered Auto-Failover During Unload
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 11: Emissions-Triggered Failover During Vehicle Unload")

for f in facilities: f.reset()

# Set F001 emissions very close to limit so the next unload triggers shutdown
f001 = next(f for f in facilities if f.facility_id == "F001")
f001.emissions = 149.0  # Limit is 150
f001.current_load = 0.0

# Prepare vehicle with enough biodegradable waste to push emissions over
v.current_load = 50.0
v.collected_waste_type = "Biodegradable"
v.location_id = "Compost Center"
v.is_available = False

# Unload → should trigger emission limit, auto-failover load to F005
success = allocator.process_vehicle_unload(v, f001)
check("Unload succeeded", success, "Unload failed")
check("F001 is now inactive (emissions exceeded)", not f001.is_active, f"is_active={f001.is_active}")

# The load should have been rerouted to F005
f005 = next(f for f in facilities if f.facility_id == "F005")
check("F005 received rerouted load from emission-triggered shutdown", 
      f005.current_load > 0, f"F005 load={f005.current_load}")

# Vehicle should be reset after successful unload
check("Vehicle load reset to 0", v.current_load == 0.0, f"Got {v.current_load}")
check("Vehicle is available again", v.is_available, f"Got {v.is_available}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 12: Full Simulation Engine Integration Test
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 12: Full Simulation Engine Integration")

bins, vehicles, facilities, graph = load_all()
engine = SimulationEngine(bins, vehicles, facilities, graph)
engine.reset_all()

# Verify engine has 8 facilities
check("Engine initialized with 8 facilities", len(engine.facilities) == 8, 
      f"Got {len(engine.facilities)}")

# Fill some bins and run optimization
engine.add_waste("B001", "Biodegradable", 90.0, user_id="TestUser")
engine.add_waste("B006", "Recyclable", 110.0, user_id="TestUser")

# Shut down F001 and F002 (primaries)
engine.facilities[0].is_active = False  # F001
engine.facilities[1].is_active = False  # F002

summary = engine.run_optimization(alert_threshold=70.0)
check("Optimization completed without crash", summary is not None, "Engine crashed!")
check("Bins were detected", summary["bins_detected"] > 0, f"Got {summary['bins_detected']}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 13: Graph Connectivity for Backup Facilities
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 13: Graph Connectivity — Backup Facility Locations Reachable")

graph = create_city_graph()

backup_locations = [
    ("South Compost Site", "South Depot"),
    ("East Recycling Yard", "Recycling Hub"),
    ("West Hazmat Depot", "Pine Heights"),
    ("North E-Waste Center", "North Depot"),
]

for loc, neighbor in backup_locations:
    dist = graph.shortest_distance(loc, neighbor)
    check(f"{loc} → {neighbor} reachable (dist={dist})", 
          dist != float('inf'), f"Got inf (unreachable)")

# Test cross-network: can vehicles reach backup from depots?
for depot in ["North Depot", "South Depot"]:
    for loc in ["South Compost Site", "East Recycling Yard", "West Hazmat Depot", "North E-Waste Center"]:
        dist = graph.shortest_distance(depot, loc)
        check(f"{depot} → {loc} reachable (dist={dist})", 
              dist != float('inf'), f"Unreachable!")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 14: Facility Status Report Includes Partner Info
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 14: Facility Status Report With Partner Info")

facilities = create_sample_facilities()
allocator = FacilityAllocator(facilities)
statuses = allocator.get_facility_statuses()

check("Status report has 8 entries", len(statuses) == 8, f"Got {len(statuses)}")

for s in statuses:
    check(f"{s['facility_id']} has partner_facility key", "partner_facility" in s,
          f"Missing partner_facility in status for {s['facility_id']}")

# F001's partner should be F005
f001_status = next(s for s in statuses if s["facility_id"] == "F001")
check("F001 status shows partner F005", f001_status["partner_facility"] == "F005",
      f"Got {f001_status['partner_facility']}")

# ═══════════════════════════════════════════════════════════════════════════════
#  TEST 15: Reset Restores All 8 Facilities
# ═══════════════════════════════════════════════════════════════════════════════
section("TEST 15: System Reset Restores All Facilities")

bins, vehicles, facilities, graph = load_all()
engine = SimulationEngine(bins, vehicles, facilities, graph)

# Mess up state
for f in engine.facilities:
    f.is_active = False
    f.current_load = 999.0
    f.emissions = 999.0
    f.redirected_count = 99

engine.reset_all()

for f in engine.facilities:
    check(f"{f.facility_id} active after reset", f.is_active, f"is_active={f.is_active}")
    check(f"{f.facility_id} load=0 after reset", f.current_load == 0.0, f"load={f.current_load}")
    check(f"{f.facility_id} emissions=0 after reset", f.emissions == 0.0, f"emissions={f.emissions}")
    check(f"{f.facility_id} redirects=0 after reset", f.redirected_count == 0, f"redirects={f.redirected_count}")

# ═══════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*70}")
print(f"  TEST RESULTS SUMMARY")
print(f"{'='*70}")
print(f"  ✅ Passed: {PASS}")
print(f"  ❌ Failed: {FAIL}")
print(f"  Total:    {PASS + FAIL}")
print(f"{'='*70}")

if FAIL == 0:
    print("\n  🎉 ALL TESTS PASSED! Facility redundancy & failover system is working correctly.\n")
else:
    print(f"\n  ⚠️  {FAIL} test(s) failed. Review output above.\n")
    sys.exit(1)

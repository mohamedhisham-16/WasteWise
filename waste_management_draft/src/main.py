# src/main.py
# CLI launcher for the WasteWise Simulation run

import random
import time
import sys
import os

# Add src to python path to resolve submodules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from simulation.data_loader import load_all
from simulation.engine import SimulationEngine
from utils import logger

def simulate_day():
    print("=== Central Command: WasteWise Simulation ===\n")
    
    # Reset all persistent logs on terminal execution
    logger.reset_all_logs()
    
    # Step 1: Initialize System with dummy data
    print("[SYSTEM] Loading city map, bins, facilities, and fleet...")
    bins, vehicles, facilities, graph = load_all()
    engine = SimulationEngine(bins, vehicles, facilities, graph)
    print(f"[SYSTEM] Loaded {len(bins)} bins, {len(vehicles)} vehicles, and {len(facilities)} facilities.")
    
    # Optional: Initial reset to ensure clean slate
    engine.reset_all()

    # Step 2: Run through several simulated time steps (e.g., hours or days)
    for step in range(1, 4):
        print(f"\n" + "="*40)
        print(f"--- TIME STEP {step} ---")
        print("="*40)
        
        # During the time step, folks randomly throw away trash
        print("\n[CITY ACTIVITY] Citizens are disposing of waste...")
        for b in bins:
            if random.random() > 0.3: # 70% chance a bin receives waste
                amount = round(random.uniform(10.0, 50.0), 2)
                engine.add_waste(b.bin_id, b.waste_type, amount, user_id=f"Virtual_{random.randint(100, 999)}")
        
        # At the end of the time step, run optimization engine
        print("\n[ENGINE TICK] Running city-wide optimization...")
        
        # Let's say bins over 70% full are considered priority.
        summary = engine.run_optimization(alert_threshold=70.0)
        
        # Pause slightly so we can read the output as it flows
        time.sleep(1) 
        
    print("\n" + "="*40)
    print("=== SIMULATION COMPLETED ===")
    print("="*40)

if __name__ == "__main__":
    # Seed random for repeatable tests
    random.seed(42)
    simulate_day()

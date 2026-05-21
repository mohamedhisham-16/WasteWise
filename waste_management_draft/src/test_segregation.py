import os
import sys

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from simulation.engine import SimulationEngine
from simulation.data_loader import load_all
from models.models import Bin

def test_segregation():
    bins, vehicles, facilities, graph = load_all()
    engine = SimulationEngine(bins, vehicles, facilities, graph)
    
    # Let's find a bin
    b1 = engine.bins[0]
    print(f"Initial Bin: {b1}")
    
    # 30kg Biodegradable, 30kg Recyclable
    engine.add_waste(b1.bin_id, "leftovers", 30.0)
    engine.add_waste(b1.bin_id, "plastics", 30.0)
    
    print(f"After adding waste - Contamination: {b1.contamination_level}")
    print(f"Bin Composition: {b1.waste_composition}")
    
    # Run optimize routing to dispatch a vehicle
    engine.run_optimization()
    
    # Let's advance facilities to process the segregated waste
    engine.advance_facilities()

if __name__ == "__main__":
    test_segregation()

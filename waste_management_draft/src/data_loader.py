# src/data_loader.py
# Module: Data Loader
# Purpose: Initializes the simulation with sample bins, vehicles, facilities, and a city graph.
# Uses only built-in Python — no external dependencies.

from models import Bin, Vehicle, Facility
from distance_graph import DistanceGraph


def create_sample_bins():
    """Creates a diverse set of waste bins across the city."""
    bins = [
        # Residential area
        Bin("B001", 100.0, "Biodegradable", "Apartment", "Node_R1"),
        Bin("B002", 80.0,  "Recyclable",    "Apartment", "Node_R1"),
        Bin("B003", 50.0,  "Hazardous",     "Apartment", "Node_R2"),

        # Hospital zone
        Bin("B004", 60.0,  "Hazardous",     "Hospital",  "Node_H1"),
        Bin("B005", 80.0,  "Biodegradable", "Hospital",  "Node_H1"),

        # Commercial district
        Bin("B006", 120.0, "Recyclable",    "Commercial", "Node_C1"),
        Bin("B007", 100.0, "Electronic",    "Commercial", "Node_C1"),
        Bin("B008", 100.0, "Biodegradable", "Market",     "Node_C2"),

        # Industrial edge
        Bin("B009", 40.0,  "Hazardous",     "Commercial", "Node_I1"),
        Bin("B010", 60.0,  "Electronic",    "Commercial", "Node_I1"),
    ]
    return bins


def create_sample_vehicles():
    """Creates a fleet of waste collection vehicles."""
    vehicles = [
        Vehicle("V001", "Compactor",       500.0, ["Biodegradable", "Recyclable"], "Depot_1"),
        Vehicle("V002", "Compactor",       400.0, ["Biodegradable", "Recyclable"], "Depot_1"),
        Vehicle("V003", "Hazmat Truck",    200.0, ["Hazardous"],                   "Depot_2"),
        Vehicle("V004", "E-Waste Carrier", 150.0, ["Electronic"],                  "Depot_2"),
        Vehicle("V005", "Mini Truck",      250.0, ["Biodegradable", "Recyclable"], "Depot_1"),
    ]
    return vehicles


def create_sample_facilities():
    """Creates processing plants for each waste category."""
    facilities = [
        Facility("F001", "Compost Unit",      1000.0, ["Biodegradable"],  0.0, "Node_F1"),
        Facility("F002", "Recycling Plant",   1500.0, ["Recyclable"],     0.0, "Node_F2"),
        Facility("F003", "Hazmat Processor",  500.0,  ["Hazardous"],      0.0, "Node_F3"),
        Facility("F004", "E-Waste Recycler",  300.0,  ["Electronic"],     0.0, "Node_F4"),
    ]
    return facilities


def create_city_graph():
    """
    Creates an urban distance graph connecting all locations.
    
    Layout (approximate):
    
        Depot_1 ---- Node_R1 ---- Node_R2 ---- Node_H1
           |             |             |            |
        Node_F1 --- Node_C1 ---- Node_C2 ---- Node_F3
           |             |             |            |
        Depot_2 ---- Node_I1 ---- Node_F2 ---- Node_F4
    """
    graph = DistanceGraph()

    # Row 1: Depot_1 — Residential — Hospital
    graph.add_edge("Depot_1",  "Node_R1", 3)
    graph.add_edge("Node_R1",  "Node_R2", 4)
    graph.add_edge("Node_R2",  "Node_H1", 2)

    # Row 2: Facility 1 — Commercial — Facility 3
    graph.add_edge("Node_F1",  "Node_C1", 5)
    graph.add_edge("Node_C1",  "Node_C2", 3)
    graph.add_edge("Node_C2",  "Node_F3", 4)

    # Row 3: Depot_2 — Industrial — Facility 2 — Facility 4
    graph.add_edge("Depot_2",  "Node_I1", 3)
    graph.add_edge("Node_I1",  "Node_F2", 6)
    graph.add_edge("Node_F2",  "Node_F4", 2)

    # Vertical connections (Column links)
    graph.add_edge("Depot_1",  "Node_F1", 4)
    graph.add_edge("Node_F1",  "Depot_2", 5)

    graph.add_edge("Node_R1",  "Node_C1", 3)
    graph.add_edge("Node_C1",  "Node_I1", 4)

    graph.add_edge("Node_R2",  "Node_C2", 2)
    graph.add_edge("Node_C2",  "Node_F2", 5)

    graph.add_edge("Node_H1",  "Node_F3", 3)
    graph.add_edge("Node_F3",  "Node_F4", 4)

    return graph


def load_all():
    """
    Convenience function: creates and returns all simulation data.
    
    Returns:
        tuple: (bins, vehicles, facilities, graph)
    """
    bins = create_sample_bins()
    vehicles = create_sample_vehicles()
    facilities = create_sample_facilities()
    graph = create_city_graph()
    return bins, vehicles, facilities, graph

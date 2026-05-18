# src/simulation/data_loader.py
# Initializes the simulation with sample bins, vehicles, facilities, and a city graph.

from models.models import Bin, Vehicle, Facility
from routing.distance_graph import DistanceGraph

def create_sample_bins():
    """Creates a diverse set of waste bins across the city."""
    bins = [
        # Greenwood Suburb (Residential)
        Bin("B001", 100.0, "Biodegradable", "Apartment", "Greenwood Suburb"),
        Bin("B002", 80.0,  "Recyclable",    "Apartment", "Greenwood Suburb"),
        Bin("B003", 50.0,  "Hazardous",     "Apartment", "Pine Heights"),

        # Metro Hospital Zone
        Bin("B004", 60.0,  "Hazardous",     "Hospital",  "Metro Hospital"),
        Bin("B005", 80.0,  "Biodegradable", "Hospital",  "Metro Hospital"),

        # Downtown Commercial
        Bin("B006", 120.0, "Recyclable",    "Commercial", "Downtown Market"),
        Bin("B007", 100.0, "Electronic",    "Commercial", "Downtown Market"),
        Bin("B008", 100.0, "Biodegradable", "Market",     "Central Plaza"),

        # Industrial Zone
        Bin("B009", 40.0,  "Hazardous",     "Commercial", "Industrial Zone"),
        Bin("B010", 60.0,  "Electronic",    "Commercial", "Industrial Zone"),
    ]
    return bins

def create_sample_vehicles():
    """Creates a fleet of waste collection vehicles."""
    vehicles = [
        Vehicle("V001", "Compactor",       500.0, ["Biodegradable", "Recyclable"], "North Depot"),
        Vehicle("V002", "Compactor",       400.0, ["Biodegradable", "Recyclable"], "North Depot"),
        Vehicle("V003", "Hazmat Truck",    200.0, ["Hazardous"],                   "South Depot"),
        Vehicle("V004", "E-Waste Carrier", 150.0, ["Electronic"],                  "South Depot"),
        Vehicle("V005", "Mini Truck",      250.0, ["Biodegradable", "Recyclable"], "North Depot"),
    ]
    return vehicles

def create_sample_facilities():
    """Creates processing plants for each waste category."""
    facilities = [
        Facility("F001", "Compost Unit",      1000.0, ["Biodegradable"],  0.0, "Compost Center"),
        Facility("F002", "Recycling Plant",   1500.0, ["Recyclable"],     0.0, "Recycling Hub"),
        Facility("F003", "Hazmat Processor",  500.0,  ["Hazardous"],      0.0, "Hazmat Disposal"),
        Facility("F004", "E-Waste Recycler",  300.0,  ["Electronic"],     0.0, "E-Waste Hub"),
    ]
    return facilities

def create_city_graph():
    """Creates an urban distance graph connecting all locations."""
    graph = DistanceGraph()

    # Row 1: North Depot — Greenwood Suburb — Pine Heights — Metro Hospital
    graph.add_edge("North Depot",  "Greenwood Suburb", 3)
    graph.add_edge("Greenwood Suburb",  "Pine Heights", 4)
    graph.add_edge("Pine Heights",  "Metro Hospital", 2)

    # Row 2: Compost Center — Downtown Market — Central Plaza — Hazmat Disposal
    graph.add_edge("Compost Center",  "Downtown Market", 5)
    graph.add_edge("Downtown Market",  "Central Plaza", 3)
    graph.add_edge("Central Plaza",  "Hazmat Disposal", 4)

    # Row 3: South Depot — Industrial Zone — Recycling Hub — E-Waste Hub
    graph.add_edge("South Depot",  "Industrial Zone", 3)
    graph.add_edge("Industrial Zone",  "Recycling Hub", 6)
    graph.add_edge("Recycling Hub",  "E-Waste Hub", 2)

    # Vertical connections (Column links)
    graph.add_edge("North Depot",  "Compost Center", 4)
    graph.add_edge("Compost Center",  "South Depot", 5)

    graph.add_edge("Greenwood Suburb",  "Downtown Market", 3)
    graph.add_edge("Downtown Market",  "Industrial Zone", 4)

    graph.add_edge("Pine Heights",  "Central Plaza", 2)
    graph.add_edge("Central Plaza",  "Recycling Hub", 5)

    graph.add_edge("Metro Hospital",  "Hazmat Disposal", 3)
    graph.add_edge("Hazmat Disposal",  "E-Waste Hub", 4)

    return graph

def load_all():
    """Convenience function: creates and returns all simulation data."""
    bins = create_sample_bins()
    vehicles = create_sample_vehicles()
    facilities = create_sample_facilities()
    graph = create_city_graph()
    return bins, vehicles, facilities, graph

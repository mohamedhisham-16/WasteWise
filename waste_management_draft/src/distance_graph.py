# src/distance_graph.py
# This module implements the Distance Matrix using a Graph (Adjacency List).
# Locations are represented as Nodes, and travel costs/times as weighted Edges.

class DistanceGraph:
    """Represents the city's urban waste collection network."""
    def __init__(self):
        # adjacency_list structure: {node_id: {neighbor_id: weight}}
        # node_id can be 'Bin1', 'FacilityA', etc.
        # weight can be distance (km) or travel time (minutes).
        self.adjacency_list = {}
        self.nodes = set()

    def add_node(self, node_id):
        """Adds a location (bin, facility, depot) to the city map."""
        if node_id not in self.adjacency_list:
            self.adjacency_list[node_id] = {}
            self.nodes.add(node_id)

    def add_edge(self, node_u, node_v, weight, bidirectional=True):
        """Connects two locations with a travel cost/distance."""
        self.add_node(node_u)
        self.add_node(node_v)
        
        self.adjacency_list[node_u][node_v] = weight
        if bidirectional:
            self.adjacency_list[node_v][node_u] = weight

    def get_distance(self, node_u, node_v):
        """Returns the travel cost between two adjacent locations."""
        if node_u in self.adjacency_list and node_v in self.adjacency_list[node_u]:
            return self.adjacency_list[node_u][node_v]
        return float('inf')  # Return infinity if no direct connection exists

    def get_neighbors(self, node_id):
        """Returns all locations directly reachable from the current one."""
        return self.adjacency_list.get(node_id, {})

    def __repr__(self):
        return f"DistanceGraph(Nodes: {len(self.nodes)}, Edges: {sum(len(v) for v in self.adjacency_list.values())})"

# src/distance_graph.py
# This module implements the Distance Matrix using a Graph (Adjacency List).
# Locations are represented as Nodes, and travel costs/times as weighted Edges.
# Includes Dijkstra's Algorithm for shortest path computation.

import heapq

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

    # --- Phase 2: Dijkstra's Shortest Path ---

    def dijkstra(self, start_node):
        """
        Computes the shortest path from start_node to ALL other nodes.
        Uses a min-heap (priority queue) for efficiency.
        
        Returns:
            distances: dict mapping each node to its shortest distance from start_node.
            previous:  dict mapping each node to its predecessor on the shortest path.
        """
        if start_node not in self.nodes:
            return {}, {}

        distances = {node: float('inf') for node in self.nodes}
        distances[start_node] = 0
        previous = {node: None for node in self.nodes}

        # Min-heap: (distance, node_id)
        priority_queue = [(0, start_node)]

        visited = set()

        while priority_queue:
            current_dist, current_node = heapq.heappop(priority_queue)

            if current_node in visited:
                continue
            visited.add(current_node)

            for neighbor, weight in self.adjacency_list.get(current_node, {}).items():
                new_dist = current_dist + weight

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_node
                    heapq.heappush(priority_queue, (new_dist, neighbor))

        return distances, previous

    def shortest_path(self, start_node, end_node):
        """
        Returns the shortest path and its total cost between two nodes.
        
        Returns:
            path: list of node IDs from start to end (empty if no path).
            cost: total travel cost (inf if no path).
        """
        distances, previous = self.dijkstra(start_node)

        if distances.get(end_node, float('inf')) == float('inf'):
            return [], float('inf')

        # Reconstruct path by backtracking from end_node
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        return path, distances[end_node]

    def shortest_distance(self, start_node, end_node):
        """Convenience method: returns just the cost of the shortest path."""
        distances, _ = self.dijkstra(start_node)
        return distances.get(end_node, float('inf'))

    def __repr__(self):
        return f"DistanceGraph(Nodes: {len(self.nodes)}, Edges: {sum(len(v) for v in self.adjacency_list.values())})"

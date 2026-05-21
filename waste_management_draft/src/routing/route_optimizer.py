# src/routing/route_optimizer.py
# Module: Multi-Bin Route Optimizer
# Purpose: Generates optimized multi-bin collection routes using Nearest-Neighbor heuristic based on Dijkstra.

def find_nearby_bins(current_bin, available_bins, graph, priority_scorer):
    """
    Finds compatible bins and ranks them based on distance and priority score.
    
    Returns:
        List of tuples: (bin_obj, distance, priority_score) sorted by:
        1. shortest distance (ascending)
        2. highest priority score (descending)
    """
    ranked_bins = []
    
    # Run Dijkstra from the current bin's location to get distances to all nodes
    distances, _ = graph.dijkstra(current_bin.location_id)
    
    for candidate in available_bins:
        # Check contamination threshold (40%)
        is_current_contaminated = getattr(current_bin, 'contamination_level', 0.0) > 0.40
        is_candidate_contaminated = getattr(candidate, 'contamination_level', 0.0) > 0.40
        
        if is_current_contaminated:
            if not is_candidate_contaminated:
                continue
        else:
            if is_candidate_contaminated or candidate.waste_type != current_bin.waste_type:
                continue
            
        dist = distances.get(candidate.location_id, float('inf'))
        if dist == float('inf'):
            continue
            
        score = priority_scorer.calculate_score(candidate)
        ranked_bins.append((candidate, dist, score))
        
    # Sort: first by shortest distance, second by highest priority score (negative for descending)
    ranked_bins.sort(key=lambda x: (x[1], -x[2]))
    return ranked_bins

def generate_collection_route(vehicle, initial_bin, available_bins, graph, priority_scorer, facility_allocator):
    """
    Generates a complete optimized route path for a vehicle starting from its current location,
    collecting the initial assigned bin, picking up nearby compatible bins, and finishing at
    the closest compatible waste processing facility.
    
    Returns:
        route_nodes: list of location IDs representing the complete route (e.g. ['Depot1', 'B101', 'B102', 'F001'])
        bins_to_collect: list of Bin objects included in this route
        total_distance: float representing the total Dijkstra distance of the route
    """
    route_nodes = [vehicle.location_id]
    bins_to_collect = []
    total_distance = 0.0
    
    # 1. Start by routing from vehicle's current location to the initial assigned bin
    current_loc = vehicle.location_id
    path_to_initial, dist_to_initial = graph.shortest_path(current_loc, initial_bin.location_id)
    
    if not path_to_initial or dist_to_initial == float('inf'):
        # No path available, cannot even collect the initial bin
        return route_nodes, bins_to_collect, total_distance
        
    route_nodes.extend(path_to_initial[1:])  # append path segments (excluding start duplicate)
    total_distance += dist_to_initial
    bins_to_collect.append(initial_bin)
    
    # Track remaining capacity and currently loaded waste
    current_load = vehicle.current_load + initial_bin.fill_level
    remaining_capacity = vehicle.total_capacity - current_load
    
    # Track current bin pointer
    current_bin = initial_bin
    current_loc = initial_bin.location_id
    
    # Create copies of available_bins to avoid mutating shared state during route planning
    pool = [b for b in available_bins if b.bin_id != initial_bin.bin_id]
    
    # 2. Heuristically search for nearby compatible bins to fill remaining capacity
    while pool:
        # Sort candidates using nearest-neighbor search
        nearby = find_nearby_bins(current_bin, pool, graph, priority_scorer)
        
        # Find the closest compatible bin that fits inside the remaining vehicle capacity
        next_bin = None
        next_dist = 0.0
        
        for candidate, dist, score in nearby:
            if candidate.fill_level <= remaining_capacity:
                next_bin = candidate
                next_dist = dist
                break
                
        if not next_bin:
            # Vehicle capacity is full or no more compatible bins can fit
            break
            
        # Add next_bin to the route
        path_to_next, dist_to_next = graph.shortest_path(current_loc, next_bin.location_id)
        if not path_to_next or dist_to_next == float('inf'):
            break
            
        route_nodes.extend(path_to_next[1:])
        total_distance += dist_to_next
        bins_to_collect.append(next_bin)
        
        # Update metrics
        current_load += next_bin.fill_level
        remaining_capacity = vehicle.total_capacity - current_load
        
        # Move pointers
        current_bin = next_bin
        current_loc = next_bin.location_id
        pool.remove(next_bin)
        
    # 3. Route from the final collection location to the closest compatible facility
    # Temporarily set vehicle state so the facility allocator knows its load and type
    orig_loc = vehicle.location_id
    orig_load = vehicle.current_load
    orig_waste = vehicle.collected_waste_type
    
    vehicle.location_id = current_loc
    vehicle.current_load = current_load
    
    # Determine the load type for the facility allocator
    if getattr(initial_bin, 'contamination_level', 0.0) > 0.40:
        vehicle.collected_waste_type = "Mixed/Contaminated"
    else:
        vehicle.collected_waste_type = initial_bin.waste_type
    
    facility = facility_allocator.allocate_facility(vehicle, graph)
    
    # Revert temporary vehicle attributes
    vehicle.location_id = orig_loc
    vehicle.current_load = orig_load
    vehicle.collected_waste_type = orig_waste
    
    if facility:
        path_to_facility, dist_to_facility = graph.shortest_path(current_loc, facility.facility_id)
        if path_to_facility and dist_to_facility != float('inf'):
            route_nodes.extend(path_to_facility[1:])
            total_distance += dist_to_facility
            
    return route_nodes, bins_to_collect, total_distance

from math import sqrt

LONGITUDE_DISTANCE = 10.29  # m/s
LATITUDE_DISTANCE = 7.55  # m/s

ROWS = 500
COLUMNS = 395


def search_path(ter_map, src_lon, src_lat, dst_lon, dst_lat):
    source = ter_map[src_lat][src_lon]
    dest = ter_map[dst_lat][dst_lon]
    parents = {}
    costs = {}
    parents[source] = None
    costs[source] = 0
    prev = None
    frontier = {}
    if source.terrain_speed > 0 and dest.terrain_speed > 0:
        current = source
        while prev != current:
            if current == dest:
                return parents, dest

            neighbors, distances = get_neighbors(current, ter_map)
            for n_idx in range(len(neighbors)):
                gn = costs[current] + get_cost(current, neighbors[n_idx], distances[n_idx])
                if (neighbors[n_idx] not in costs) or (gn < costs[neighbors[n_idx]]):
                    costs[neighbors[n_idx]] = gn
                    fn = gn + get_heuristic(neighbors[n_idx], dest)
                    parents[neighbors[n_idx]] = current
                    frontier[neighbors[n_idx]] = fn
            prev = current
            current = sorted(frontier, key=frontier.get)[0]
            del frontier[current]

    return None, None


def get_cost(start, end, distance):
    alt_delta = start.alt - end.alt  # + is good
    terrain_delta = (start.terrain_speed + end.terrain_speed) / 2.0
    dist_3d = sqrt(distance ** 2 + alt_delta ** 2)
    time = dist_3d / (terrain_delta + (alt_delta / 40.0))
    return time


def get_heuristic(start, dest):
    return sqrt((start.lon - dest.lon) ** 2 + (start.lat - dest.lat) ** 2 + (
        start.alt - dest.alt) ** 2) / max(start.terrain_speed, dest.terrain_speed)  # Best terrain speed


def get_neighbors(node, ter_map):
    neighbors = []
    distances = []
    y = node.lon - 1
    x = node.lat
    if -1 < x < COLUMNS and -1 < y < ROWS:
        neighbor = ter_map[x][y]
        if neighbor.terrain_speed > 0:
            neighbors.append(neighbor)
            distances.append(LONGITUDE_DISTANCE)

    y = node.lon
    x = node.lat - 1
    if -1 < x < COLUMNS and -1 < y < ROWS:
        neighbor = ter_map[x][y]
        if neighbor.terrain_speed > 0:
            neighbors.append(neighbor)
            distances.append(LATITUDE_DISTANCE)

    y = node.lon + 1
    x = node.lat
    if -1 < x < COLUMNS and -1 < y < ROWS:
        neighbor = ter_map[x][y]
        if neighbor.terrain_speed > 0:
            neighbors.append(neighbor)
            distances.append(LONGITUDE_DISTANCE)

    y = node.lon
    x = node.lat + 1
    if -1 < x < COLUMNS and -1 < y < ROWS:
        neighbor = ter_map[x][y]
        if neighbor.terrain_speed > 0:
            neighbors.append(neighbor)
            distances.append(LATITUDE_DISTANCE)

    return neighbors, distances

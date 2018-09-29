class Node:
    __slots__ = 'lon', 'lat', 'alt', 'terrain_speed'

    def __init__(self, lon, lat, alt, terrain_speed):
        self.lon = lon
        self.lat = lat
        self.alt = alt
        self.terrain_speed = terrain_speed

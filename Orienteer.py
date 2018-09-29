from PIL import Image
from Node import Node
from Astar import search_path as search
import time

TERRAINS = {(248, 148, 18): 'open_land', (255, 192, 0): 'rough_meadow', (255, 255, 255): 'easy_forest',
            (2, 208, 60): 'slow_forest', (2, 136, 40): 'walk_forest', (5, 73, 24): 'impass_veg',
            (0, 0, 255): 'water', (71, 51, 3): 'road', (0, 0, 0): 'sidewalk', (205, 0, 101): 'out_of_bounds'}

# Baseline for all other seasons
SUMMER_TERRAINS = {'open_land': 1.66, 'rough_meadow': 0.916, 'easy_forest': 0.75, 'slow_forest': 0.41,
                   'walk_forest': 0.3,
                   'impass_veg': 0, 'water': 0, 'road': 1.33, 'sidewalk': 1.25, 'out_of_bounds': 0}

# Easy forest is slower here
FALL_TERRAINS = {'open_land': 1.66, 'rough_meadow': 0.916, 'easy_forest': 0.41, 'slow_forest': 0.41, 'walk_forest': 0.3,
                 'impass_veg': 0, 'water': 0, 'road': 1.33, 'sidewalk': 1.25, 'out_of_bounds': 0}


def is_land(row, col, img):
    cols, rows = img.size
    if -1 < col < cols and -1 < row < rows:
        if TERRAINS[img.getpixel((col, row))[:3]] != 'water':
            return True
        else:
            return False


def is_water(row, col, img, alt, elevations):
    cols, rows = img.size
    if -1 < col < cols and -1 < row < rows:
        if TERRAINS[img.getpixel((col, row))[:3]] == 'water' and abs(float(elevations[row][col]) - alt) <= 1.0:
            return True
        else:
            return False


def get_winter_terrain(row, col, img):
    for pix in range(7, 0, -1):
        if is_land(row + pix, col, img) or is_land(row, col + pix, img) or is_land(row - pix, col, img) or is_land(row,
                                                                                                                   col - pix,
                                                                                                                   img):
            return 0.9
    return 0.0


def get_spring_terrain(row, col, alt, elevations, img):
    for pix in range(15):
        if is_water(row + pix, col, img, alt, elevations) or is_water(row, col + pix, img, alt, elevations) or is_water(
                        row - pix, col, img, alt, elevations) or is_water(row, col - pix, img, alt, elevations):
            return 0.0
    return None


def prepare_map(img, filename, season):
    cols, rows = img.size

    lines = open(filename).readlines()
    terrain_speed = {}
    terrain_map = []
    waters = []
    muds = []
    elevations = []
    for row in range(rows):
        line = lines[row].strip().split()[:cols]
        elevations.append(line)

    for row in range(rows):
        node_row = []
        for col in range(cols):
            color = img.getpixel((col, row))[:3]
            alt = float(elevations[row][col])
            if season == 'summer':
                terrain_speed = SUMMER_TERRAINS[TERRAINS[color]]
            elif season == 'fall':
                terrain_speed = FALL_TERRAINS[TERRAINS[color]]
            elif season == 'winter':
                if TERRAINS[color] == 'water':
                    terrain_speed = get_winter_terrain(row, col, img)
                    if terrain_speed != 0.0:
                        waters.append((col, row))
                else:
                    terrain_speed = SUMMER_TERRAINS[TERRAINS[color]]
            elif season == 'spring':
                if TERRAINS[color] != 'water':
                    terrain_speed = get_spring_terrain(row, col, alt, elevations, img)
                    if terrain_speed is None:
                        terrain_speed = SUMMER_TERRAINS[TERRAINS[color]]
                    else:
                        muds.append((col, row))
                else:
                    terrain_speed = SUMMER_TERRAINS[TERRAINS[color]]
            else:
                print('Wrong season. exit?')
            node = Node(col, row, alt, terrain_speed)
            node_row.append(node)
        terrain_map.append(node_row)
    if season == 'winter':
        for coord in waters:
            img.putpixel(coord, (100, 200, 255))
        img.save('winter.png')

    if season == 'spring':
        for coord in muds:
            img.putpixel(coord, (255, 255, 0))
        img.save('spring.png')

    return terrain_map


def write_im(img, nodes, dst, filename):
    if nodes is not None:
        while dst is not None:
            img.putpixel((dst.lon, dst.lat), (205, 0, 101))
            dst = nodes[dst]
        img.save(filename)
    return img


def main():
    img = Image.open('terrain.png')
    filename = 'mpp.txt'
    season = input('Please enter season. Eg: summer, fall, winter, spring')
    season_map = prepare_map(img, filename, season)
    if season == 'winter':
        winter_img = Image.open('winter.png')
    if season == 'spring':
        spring_img = Image.open('spring.png')
    testfile = input('Please enter control file. Eg: white.txt, brown.txt, red.txt')
    lines = open(testfile).readlines()
    sx, sy = lines[0].strip().split()

    for i in range(len(lines) - 1):
        dx, dy = lines[i + 1].strip().split()
        path, dest = search(season_map, int(sx), int(sy), int(dx), int(dy))
        sx, sy = dx, dy
        if path is None:
            break
        if season == 'winter':
            output_img = write_im(winter_img, path, dest, 'winter_output.png')
        elif season == 'spring':
            output_img = write_im(spring_img, path, dest, 'spring_output.png')
        elif season == 'fall':
            output_img = write_im(img, path, dest, 'fall_output.png')
        else:
            output_img = write_im(img, path, dest, season + 'summer_output.png')

    output_img.show()

if __name__ == '__main__':
    main()

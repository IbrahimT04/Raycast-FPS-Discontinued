""" Made my Ibrahim Tariq from Ontario, Canada. """

import math
import time
from math import sin, cos
import pygame
import random

import ctypes
import numpy as np  # For efficient array handling

import platform
print(platform.architecture())

# Load the DLL
compute_lib = ctypes.CDLL("./dll/libcompute.dll")

# Define the function signature of heavy_computation
# Adjust argtypes and restype based on the actual C++ function
compute_lib.heavy_computation.argtypes = [
    ctypes.c_int,  # nScreenWidth
    ctypes.c_int,  # nScreenHeight
    ctypes.c_float,  # fPlayerX
    ctypes.c_float,  # fPlayerY
    ctypes.c_float,  # fPlayerA
    ctypes.c_float,  # fFOV
    ctypes.POINTER(ctypes.c_char),  # g_map (char array)
    ctypes.c_int,  # nMapWidth
    ctypes.c_int,  # nMapHeight
    ctypes.c_float,  # vertical_angle
    ctypes.c_float,  # scope
    ctypes.c_float,  # fDepth
    ctypes.POINTER(ctypes.c_int)  # Output screen buffer
]

compute_lib.heavy_computation.restype = ctypes.POINTER(ctypes.c_int)  # Returns screen output as int pointer

score = 0

# For Pixel Size Graphics Settings
# ---> Low Graphics = 15
# ---> Medium Graphics = 8
# ---> High Graphics = 4
# ---> Ultra Graphics = 3
# ---> Max Graphics = 2
pixel_size = 8

nMapWidth = 16
nMapHeight = 16

fPlayerX = 8.00
fPlayerY = 14.00
fPlayerA = 0.0
zoom_FOV = math.pi / 7.0
no_zoom_FOV = math.pi / 4.0
fFOV = math.pi / 4.0  # Not editable
fDepth = 16.0
fSpeed = 3.0
fEnemySpeed = 0.25
fBulletSpeed = 7
elapsedTime = 0  # Not editable
agro_range = 10

scope = 0  # Not editable
vertical_angle = 0  # Not editable

h_indent = 2
v_indent = 2
buffer = 2
map_size = 4


g_map = "#######$$#######"
g_map += "#*+.#.*+.......#"
g_map += "#...#########..#"
g_map += "#...#*...#..#..#"
g_map += "#...##...#.....#"
g_map += "#...#..+.......#"
g_map += "#...#######....#"
g_map += "#........*#....#"
g_map += "#..#####.......#"
g_map += "#....*.#########"
g_map += "#..............#"
g_map += "#....#####.....#"
g_map += "#+...#.........#"
g_map += "#.*..#.........#"
g_map += "#....#.........#"
g_map += "################"

# Test map
"""
g_map = "..............*."
g_map += ".#.............."
g_map += ".............#.."
g_map += "................"
g_map += "................"
g_map += "................"
g_map += "................"
g_map += "................"
g_map += "................"
g_map += "................"
g_map += "..#............."
g_map += "................"
g_map += "................"
g_map += ".....#.........."
g_map += "..............#."
g_map += "................"
"""

# Create a ctypes string buffer from g_map
g_map_c = ctypes.create_string_buffer(g_map.encode('utf-8'))

tp1 = time.time()
tp2 = time.time()


class Enemy:
    enemies = []

    def __init__(self, level, x, y):
        self.level = level
        self.x = x
        self.y = y
        Enemy.enemies.append(self)

    def update(self, player_x, player_y):
        x_diff = player_x - self.x
        y_diff = player_y - self.y
        dist = math.sqrt(x_diff ** 2 + y_diff ** 2)
        if dist < agro_range:
            self.move(x_diff / dist, y_diff / dist)

    def move(self, v_x, v_y):
        multiplier = 2 if self.level == 1 else 1
        x_new = self.x + v_x * fSpeed * elapsedTime * fEnemySpeed * multiplier
        y_new = self.y + v_y * fSpeed * elapsedTime * fEnemySpeed * multiplier
        if g_map[int(x_new) + nMapWidth * int(self.y)] != '#' and abs(x_new - self.x) <= 1:
            self.x = x_new
        if g_map[int(self.x) + nMapWidth * int(y_new)] != '#' and abs(y_new - self.y) <= 1:
            self.y = y_new


class Bullet:
    def __init__(self, x, y, z, vx, vy, vz):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

    def move(self):
        global fSpeed, elapsedTime
        self.x += self.vx * fSpeed * elapsedTime
        self.y += self.vy * fSpeed * elapsedTime
        self.z += self.vz * fSpeed * elapsedTime


def update_map(x, y, status):
    global g_map
    temp_map = list(g_map)
    if status == -1:
        temp_map[x + nMapWidth * y] = "-"
    elif status == 4:
        temp_map[x + nMapWidth * y] = "="
    elif status == 3:
        temp_map[x + nMapWidth * y] = "*"
    elif status == 2:
        temp_map[x + nMapWidth * y] = "+"
    else:
        temp_map[x + nMapWidth * y] = "."
    g_map = "".join(temp_map)


def check_collisions(x, y, z=0.0):
    global g_map, score, elapsedTime
    distance = math.sqrt((int(x) + 0.5 - x) ** 2 + (int(y) + 0.5 - y) ** 2 + (int(z * 1.25)) ** 2)
    distance_xy = math.sqrt((int(x) + 0.5 - x) ** 2 + (int(y) + 0.5 - y) ** 2)
    if x < 0.0 or x > nMapWidth:
        return False
    elif y < 0.0 or y > nMapHeight:
        return False
    elif z < -2.0 or z > 4.0:
        return False
    elif g_map[int(x) + nMapWidth * int(y)] == "#" and -1.0 < z < 1.0:
        return False
    elif g_map[int(x) + nMapWidth * int(y)] == "=" and distance < 0.5:
        update_map(int(x), int(y), 3)
        elapsedTime = 0
        score += 1
        return False
    elif g_map[int(x) + nMapWidth * int(y)] == "*" and distance < 0.5:
        update_map(int(x), int(y), 2)
        elapsedTime = 0
        return False
    elif g_map[int(x) + nMapWidth * int(y)] == "+" and -0.5 < z < 0.5 and distance_xy < 0.15:
        update_map(int(x), int(y), 1)
        elapsedTime = 0
        score += 1
        return False
    else:
        return True


def display_map():
    global screen, fPlayerA, fFOV, g_map
    size = map_size / math.sqrt(pixel_size) if pixel_size < 5 else map_size * 4 / pixel_size

    for i in range(int(size * (-buffer)), int(size * (nMapWidth + buffer))):
        for j in range(int(size * (-buffer)), int(size * (nMapHeight + buffer))):
            color = 0, 0, 100
            if i < 0 or j < 0 or i >= nMapWidth * size or j >= nMapHeight * size:
                color = 50, 20, 80
            else:
                my_char = g_map[int(i // size) + nMapWidth * int(j // size)]
                if i // size == int(fPlayerX) and j // size == int(fPlayerY):
                    color = 0, 255, 0
                elif my_char == "+" or my_char == "=" or my_char == "*":
                    for a in range(int(i/size - 1.0), int(i/size + 2.0)):
                        for b in range(int(j/size - 1.0), int(j/size + 2.0)):
                            if g_map[a + b * nMapWidth] == "-":
                                if my_char == "+":
                                    color = 200, 100, 0
                                elif my_char == "=":
                                    color = 200, 50, 0
                                elif my_char == "*":
                                    color = 200, 0, 0
                                break
                        else:
                            continue
                        break
                elif my_char == "#":
                    color = 200, 200, 200
                elif my_char == "$":
                    color = 200, 200, 0
                elif my_char == "-":
                    color = 0, 20, 150
                else:
                    color = 0, 0, 100

            screen[i + int(h_indent * size)][j + int(v_indent * size)] = color


def create_enemies():
    for i in range(0, nMapWidth):
        for j in range(0, nMapHeight):
            if g_map[i + nMapWidth * j] == "*":
                Enemy(2, i, j)
            elif g_map[i + nMapWidth * j] == "+":
                Enemy(1, i, j)
            elif g_map[i + nMapWidth * j] == "=":
                Enemy(1, i, j)
                Enemy(2, i, j)


def update_enemies():
    # Erase Enemies
    for i in range(nMapWidth * nMapHeight):
        if g_map[i] == "*" or g_map[i] == "+" or g_map[i] == "=" or g_map[i] == "-":
            update_map(i, 0, 1)
    # Update enemy locations
    for i in Enemy.enemies:
        i.update(fPlayerX, fPlayerY)
    # Add Enemies to Map
    for i in Enemy.enemies:
        if g_map[int(i.x) + nMapWidth * int(i.y)] == "+" or g_map[int(i.x) + nMapWidth * int(i.y)] == "*":
            update_map(int(i.x), int(i.y), 4)
        else:
            update_map(int(i.x), int(i.y), i.level + 1)


def main():
    global tp2, tp1, fPlayerX, fPlayerY, fPlayerA, elapsedTime, scope, vertical_angle, screen, run, win

    tp2 = time.time()

    if elapsedTime == 0:
        Enemy.enemies = []
        create_enemies()

    elapsedTime = tp2 - tp1
    tp1 = tp2

    update_enemies()

    # Ray-casting calculations
    # Call the C++ heavy_computation function via ctypes instead of doing raycasting in Python
    compute_lib.heavy_computation(
        nScreenWidth,
        nScreenHeight,
        ctypes.c_float(fPlayerX),
        ctypes.c_float(fPlayerY),
        ctypes.c_float(fPlayerA),
        ctypes.c_float(fFOV),
        g_map_c,
        nMapWidth,
        nMapHeight,
        ctypes.c_float(vertical_angle),
        ctypes.c_float(scope),
        ctypes.c_float(fDepth),
        screen_output_c
    )

    # Convert the result back to a 3D numpy array (RGB color values)
    output_array = np.ctypeslib.as_array(screen_output_c, shape=(nScreenHeight, nScreenWidth, 3))

    # Use the output_array to render the screen
    for y in range(nScreenHeight):
        for x in range(nScreenWidth):
            color = tuple(output_array[y][x])  # Extract RGB color
            screen[x][y] = color

    # Display Addons
    for i in range(fBulletSpeed):
        for bul in bullets:
            x, y, z = bul.x, bul.y, bul.z
            if not check_collisions(x, y, z):
                bullets.remove(bul)
                del bul
            else:
                bul.move()

    display_bullets()

    display_map()

    if (g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "*"
            or g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "+"
            or g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "="):
        run = False
    elif g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "$":
        win = True
        run = False

    for y in range(0, nScreenHeight):
        for x in range(0, nScreenWidth):
            pixel = pygame.Rect((x * pixel_size, y * pixel_size, pixel_size, pixel_size))
            pygame.draw.rect(screen2, "#{:02x}{:02x}{:02x}".format(*screen[x][y]), pixel)
    print(1 / elapsedTime if elapsedTime != 0.0 else 0)


def display_bullets():
    global bullets, screen, fPlayerA, fFOV, g_map
    vertical_fov = fFOV * nScreenHeight / nScreenWidth
    for bul in bullets:
        x, y, z = bul.x, bul.y, bul.z
        VectorX_b, VectorY_b, VectorZ_b = x - fPlayerX, y - fPlayerY, z
        VectorX_p, VectorY_p, VectorZ_p = cos(fPlayerA), sin(fPlayerA), 0.6877944 * vertical_angle / 100.0

        VectorB_len_xy = math.sqrt(VectorX_b ** 2 + VectorY_b ** 2)

        # To not see bullets through walls
        path_check = True
        fx, fy = fPlayerX, fPlayerY
        stepX = True if abs(VectorX_b) > abs(VectorY_b) else False
        while int(fx) != int(x) and int(fy) != int(y) and 0 < fx < 16 and 0 < fy < 16:
            if g_map[int(fx) + nMapWidth * int(fy)] == "#":
                path_check = False
                break
            fx += 0.25 * VectorX_b/VectorB_len_xy if stepX else 0.25 * VectorX_b / (VectorY_b * VectorB_len_xy)
            fy += 0.25 * VectorY_b / (VectorX_b * VectorB_len_xy) if stepX else 0.25 * VectorY_b/VectorB_len_xy

        if not path_check:
            continue

        cross_z = VectorX_b * VectorY_p - VectorX_p * VectorY_b
        vertical_theta = math.atan(VectorZ_b / VectorB_len_xy) - VectorZ_p if VectorB_len_xy > 0.005 else 0.0
        cross_buffer = 0
        theta = 0.0

        if VectorB_len_xy > 1.0:
            cross_buffer = 20.0 / VectorB_len_xy + 3.0 + scope / 2
            sin_theta = cross_z / VectorB_len_xy
            if abs(sin_theta) > 0.9995:
                theta = math.pi / 2
            elif abs(sin_theta) > 0.005:
                theta = math.asin(sin_theta)

        if abs(theta) < fFOV / 2.0 and abs(vertical_theta) < vertical_fov / 2.0:
            hor_cord = nScreenWidth / 2.0 - theta * nScreenWidth / fFOV
            ver_cord = nScreenHeight / 2.0 - vertical_theta * nScreenHeight / vertical_fov
            for i in range(int(ver_cord - cross_buffer), int(ver_cord + cross_buffer)):
                for j in range(int(hor_cord - cross_buffer), int(hor_cord + cross_buffer)):
                    dis = math.sqrt((i - ver_cord) ** 2 + (j - hor_cord) ** 2)
                    if dis <= cross_buffer / 2.0 and 0 < j < nScreenWidth and 0 < i < nScreenHeight:
                        if VectorB_len_xy < 2.0:
                            screen[j][i] = (255, 255, 0)
                        elif dis > 5.0:
                            screen[j][i] = (255, random.randint(100, 255), 0)
                        elif dis < cross_buffer / 4.0:
                            screen[j][i] = (200, 125, 0)
                        else:
                            screen[j][i] = (150, 90, 0)


def move(direction):
    global fPlayerX, fPlayerY, fPlayerA, elapsedTime, g_map, nMapWidth

    if fPlayerX < 0.0:
        fPlayerX = 0.0
    elif fPlayerX > nMapWidth - 1.0:
        fPlayerX = nMapWidth - 1.0
    if fPlayerY < 0.0:
        fPlayerY = 0.0
    elif fPlayerY > nMapHeight - 1.0:
        fPlayerY = nMapHeight - 1.0
    if direction == 's_left':
        fPlayerA -= (fSpeed * 1.00) * elapsedTime
    elif direction == 's_right':
        fPlayerA += (fSpeed * 1.00) * elapsedTime
    elif direction == 'right':
        fPlayerY += cos(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerY -= cos(fPlayerA) * fSpeed * elapsedTime
        fPlayerX -= sin(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerX += sin(fPlayerA) * fSpeed * elapsedTime
    elif direction == 'left':
        fPlayerY -= cos(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerY += cos(fPlayerA) * fSpeed * elapsedTime
        fPlayerX += sin(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerX -= sin(fPlayerA) * fSpeed * elapsedTime
    elif direction == 'forward':
        fPlayerX += cos(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerX -= cos(fPlayerA) * fSpeed * elapsedTime
        fPlayerY += sin(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerY -= sin(fPlayerA) * fSpeed * elapsedTime
    elif direction == 'back':
        fPlayerX -= cos(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerX += cos(fPlayerA) * fSpeed * elapsedTime
        fPlayerY -= sin(fPlayerA) * fSpeed * elapsedTime
        if g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == '#':
            fPlayerY += sin(fPlayerA) * fSpeed * elapsedTime


def look(angle):
    global fPlayerA, elapsedTime, nMapWidth, center, vertical_angle
    diff = angle[0] - center[0]
    v_diff = angle[1] - center[1]
    if abs(diff) != 0:
        fPlayerA += (fSpeed * 0.80) * elapsedTime * diff * pixel_size / 120
    if abs(v_diff) != 0:
        vertical_angle -= (fSpeed * 0.80) * elapsedTime * v_diff * pixel_size / 4
        if vertical_angle > 100 or vertical_angle < -100:
            vertical_angle += (fSpeed * 0.80) * elapsedTime * v_diff * pixel_size / 4
            # +100 to -100 units == +0.6877944 to - 0.6877944 radians


def event_checker(events):
    global run, s_left, s_right, left, right, forward, back, escape, zoom, scope, resized
    for event in events:
        # Exit
        if event.type == pygame.QUIT:
            run = False
        # Mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Right click
            if event.button == 3:
                scope = 10
                zoom = True
            # Left click
            elif event.button == 1 and len(bullets) < 3:
                add_bullet()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                scope = 0
                zoom = False
        # Keyboard inputs
        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE and event.type == pygame.KEYDOWN:
                escape = not escape
            if event.key == pygame.K_TAB and event.type == pygame.KEYDOWN:
                resized = True
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left = not left
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right = not right
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                forward = not forward
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                back = not back
            if event.key == pygame.K_q:
                s_left = not s_left
            if event.key == pygame.K_e:
                s_right = not s_right


def add_bullet():
    global bullets, vertical_angle
    fvX = cos(fPlayerA)
    fvY = sin(fPlayerA)
    fvZ = 0.6877944 * vertical_angle / 100.0
    v_len = math.sqrt(fvX ** 2 + fvY ** 2 + fvZ ** 2)
    shot = Bullet(fPlayerX, fPlayerY, 0.0, fvX / v_len, fvY / v_len, fvZ / v_len)
    bullets.append(shot)


pygame.init()

screen2 = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
nFullScreenWidth, nFullScreenHeight = screen2.get_size()
nScreenWidth = int(nFullScreenWidth / pixel_size)
nScreenHeight = int(nFullScreenHeight / pixel_size)

screen = [[() for i in range(nScreenHeight)] for j in range(nScreenWidth)]
bullets = []


resized = True
load_enemy = False
zoom = False
s_left = False
s_right = False
left = False
right = False
forward = False
back = False
escape = False
run = True
win = False

try:
    pygame.mouse.set_cursor(pygame.cursors.broken_x)
except pygame.error:
    print("Cursor setting is not supported in this environment")
    run = False

white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)

center = (int(nScreenWidth * pixel_size / 2), int(nScreenHeight * pixel_size / 2))

font = pygame.font.Font('freesansbold.ttf', 32)
text = font.render('+', True, white)
textRect = text.get_rect()
textRect.center = center
textScore = text.get_rect()
textScore.topright = (nScreenWidth * pixel_size - 160, 10)
textMag = text.get_rect()
textMag.bottomright = (nScreenWidth * pixel_size - 40, nScreenHeight * pixel_size)


while run:

    # Create a buffer for the output screen
    screen_output = np.zeros((nScreenHeight * nScreenWidth * 3), dtype=np.int32)  # RGB buffer
    screen_output_c = screen_output.ctypes.data_as(ctypes.POINTER(ctypes.c_int))

    if resized:
        if nScreenWidth != int(225 * 4 / pixel_size) and nScreenHeight != int(150 * 4 / pixel_size):
            nScreenWidth = int(225 * 4 / pixel_size)
            nScreenHeight = int(150 * 4 / pixel_size)
            screen2 = pygame.display.set_mode((nScreenWidth * pixel_size, nScreenHeight * pixel_size),
                                              pygame.DOUBLEBUF)
        else:
            screen2 = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
            nScreenWidth = int(nFullScreenWidth / pixel_size)
            nScreenHeight = int(nFullScreenHeight / pixel_size)
        center = (int(nScreenWidth * pixel_size / 2), int(nScreenHeight * pixel_size / 2))
        textRect.center = center
        textScore.topright = (nScreenWidth * pixel_size - 190, 10)
        textMag.bottomright = (nScreenWidth * pixel_size - 60, nScreenHeight * pixel_size)
        resized = False
    else:
        main()
    if s_left:
        move('s_left')
    if s_right:
        move('s_right')
    if left:
        move('left')
    if right:
        move('right')
    if forward:
        move('forward')
    if back:
        move('back')
    if zoom:
        fFOV = zoom_FOV
    else:
        fFOV = no_zoom_FOV

    pos = pygame.mouse.get_pos()

    if not escape:
        if pos != center:
            look(pos)
            pygame.mouse.set_pos(center)

    pygame.mouse.set_visible(escape)

    event_checker(pygame.event.get())

    screen2.blit(text, textRect)

    my_score = font.render(('SCORE = ' + str(score)), True, green)
    screen2.blit(my_score, textScore)

    my_mag = font.render((str(3 - len(bullets)) + "/3"), False, (0, 0, 0))
    screen2.blit(my_mag, textMag)

    pygame.display.flip()

pygame.quit()

if win:
    print("You WON\nYour score is", score)
else:
    print("You LOST\nYour score is", score)

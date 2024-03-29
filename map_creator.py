import os
import os.path
import os
import glob
import time
import random
import numpy
import game_info
from math import ceil
from PIL import (
    Image,
    ImageFont,
    ImageDraw,
)
from discord.ext import commands

#
#  ________                                   __              _____                 
# /  _____/  ____   ____   ________________ _/  |_  ____     /     \ _____  ______  
#/   \  ____/ __ \ /    \_/ __ \_  __ \__  \\   __\/ __ \   /  \ /  \\__  \ \____ \ 
#\    \_\  \  ___/|   |  \  ___/|  | \// __ \|  | \  ___/  /    Y    \/ __ \|  |_> >
# \______  /\___  >___|  /\___  >__|  (____  /__|  \___  > \____|__  (____  /   __/ 
#        \/     \/     \/     \/           \/          \/          \/     \/|__|
#

async def generate_map(raw_data, level):

    try:
        #Definitions
        file_name = "./player_files/active_" + str(raw_data.author.id) + ".txt"
        walls = "#"
        floor = " "
        void = "-"
        player = "&"

        #set up width and height
        room_width, room_height= (40,40)

        #First set the entire grid to void characters
        grid_array = [[void for i in range(room_height)] for j in range(room_width)]

        #Create the controller in the middle of the room
        controller_x = int(room_width / 2)
        controller_y = int(room_height / 2)
        player_x = controller_x
        player_y = controller_y
        #random direction with:
        #0 = north
        #1 = east
        #2 = south
        #3 = west
        direction = random.randint(0,3) 
        #create steps for how large you want the room to be (try to not have it be larger than the total square footage of the space)
        steps = room_width * room_height
        direction_change_odds = 1

        for x in range(steps):
            grid_array[controller_y][controller_x] = floor
            x_direction = 0
            y_direction = 0
            #randomize the direction
            if(random.randint(0,direction_change_odds) == direction_change_odds):
                direction = random.randint(0,3)
            
            #move the controller
            if direction == 0:
                y_direction = -1
            elif direction ==1:
                x_direction = 1
            elif direction == 2:
                y_direction = 1
            elif direction == 3:
                x_direction = -1
            
            controller_x += x_direction
            controller_y += y_direction
            
            #Ensure that we didn't go outside the grid
            if(controller_x < 2 or controller_x >= room_width - 2):
                controller_x += -x_direction * 2
            if(controller_y < 2 or controller_y >= room_height - 2):
                controller_y += -y_direction * 2

        for y in range(1,room_height-1):
            for x in range(1,room_height-1):
                if grid_array[y][x] != floor:
                    top = grid_array[y-1][x]
                    left = grid_array[y][x-1]
                    right = grid_array[y][x+1]
                    bottom = grid_array[y+1][x]
                    if top == floor or left == floor or right == floor or bottom == floor:
                        grid_array[y][x] = walls

        grid_array[player_y][player_x] = player

        #okay now that we have the player and everything inside of the grid... Let's start placing enemies
        #I'm gonna have to redo the entire file nameing system if I want to load in a level as dictated on that sheet
        #unless I throw the level inside a stats page... Could do that... I'll think about it.
        #First anyways I'm just gonna spawn some basic enemies into a level and disregard difficulty scale according to level
        enemy_dict = {
            "m" : ["m", '1', '6', '0', '1', '0', '0', '0', '-1', '-1', '-1', '4', '0'],
            "b" : ["b", '2', '5', '0', '1', '0', '0', '0', '-1', '-1', '-1', '2', '0'],
            "f" : ["f", '2', '5', '1', '1', '0', '0', '0', '-1', '-1', '-1', '4', '0'],
            "s" : ["s", '2', '5', '0', '1', '0', '0', '0', '-1', '-1', '-1', '2', '0'],
            "w" : ["w", '6', '15', '2', '3', '0', '0', '0', '-1', '-1', '-1', '0', '0'], # Need
            "S" : ["S", '10', '45', '5', '5', '0', '0', '0', '-1', '-1', '-1', '0', '0'], # to
            "I" : ["I", '13', '55', '7', '7', '0', '0', '0', '-1', '-1', '-1', '0', '0'], # work
            "W" : ["W", '17', '65', '10', '9', '0', '0', '0', '-1', '-1', '-1', '0', '0'], # on
            "!" : ["!", '26', '100', '20', '10', '0', '0', '0', '-1', '-1', '-1', '0', '0'], # these
            "?" : ["?", '0', '0', '0', '0', '2', '0', '0', '-1', '-1', '-1', '0', '0'],
            "<" : ["<", '0', '0', '0', '0', '1', '0', '0', '-1', '-1', '-1', '0', '0']
        }
        enemy_list = [
            "m",
            "b",
            "f",
            "s",
            "w",
            "S",
            "I",
            "W"
        ]

        amount_of_enemies = level * random.randint(1,5)
        amount_of_items = (level * random.randint(1,2)) + 1 #Items spawns are going to be based on the level you're on, and there'll only be one door per level
        player_info = ["&", "3", "10", "1", level, "0", "1", "1", player_x, player_y, "0", "-1", "0"]
        info_array = [[void for i in range(len(player_info) + 1)] for j in range(amount_of_enemies + amount_of_items + 1)]
        for entity_val in range(amount_of_enemies + amount_of_items + 1):
            info_array[entity_val][0] = str(entity_val + 1)
        for x in range(len(player_info)):
            info_array[0][x+1] = player_info[x]
        for x in range(amount_of_enemies):
            if level < 3:
                max_enemy_type = 3
            elif level >=3 and level < 5:
                max_enemy_type = 4
            elif level >=5 and level < 7:
                max_enemy_type = 5
            elif level >=7 and level < 9:
                max_enemy_type = 6
            elif level == 9:
                max_enemy_type = 7

            enemy_val = random.randint(0, max_enemy_type)
            enemy_character = enemy_list[enemy_val]
            enemy_stats = enemy_dict[enemy_character]
            enemy_y = random.randint(0,room_height-1)
            enemy_x = random.randint(0,room_width-1)
            if abs(enemy_y - player_y) <= 3 and abs(enemy_x - player_x) <= 3:
                enemy_x += (random.randint(0,1)*2-1) * 3
                enemy_y += (random.randint(0,1)*2-1) * 3
            while grid_array[enemy_y][enemy_x] != " ":
                enemy_x += random.randint(0,1)*2-1
                enemy_y += random.randint(0,1)*2-1
                if enemy_y < 1:
                    enemy_y += 2
                if enemy_y > (room_height - 2):
                    enemy_y -= 2
                if enemy_x < 1:
                    enemy_x += 2
                if enemy_x > (room_width - 2):
                    enemy_x -= 2
                if abs(enemy_y - player_y) <= 3 and abs(enemy_x - player_x) <= 3:
                    enemy_x += (random.randint(0,1)*2-1) * 3
                    enemy_y += (random.randint(0,1)*2-1) * 3
            grid_array[abs(enemy_y)][abs(enemy_x)] = enemy_character
            for y in range(len(enemy_stats)):
                if y == 8:
                    info_array[x+1][y+1] = enemy_x
                elif y == 9:
                    info_array[x+1][y+1] = enemy_y
                elif y == 10:
                    next_direction = random.randint(0,3)
                    info_array[x+1][y+1] = next_direction
                else:
                    info_array[x+1][y+1] = enemy_stats[y]
        for x in range(amount_of_items):
            #First value is going to be the door and then we'll spawn in the items
            if x > 0:
                item_stats = enemy_dict["?"]
                item_y = random.randint(0,room_height-1)
                item_x = random.randint(0,room_width-1)
                #I think we want to spawn items with the same rules as enemies
                #3 spaces around the player on all directions nothing can init spawn
                if abs(item_y - player_y) <= 3 and abs(item_x - player_x) <= 3:
                    item_x += (random.randint(0,1)*2-1) * 3
                    item_y += (random.randint(0,1)*2-1) * 3
                while grid_array[abs(item_y)][abs(item_x)] != " ":
                    item_x += random.randint(0,1)*2-1
                    item_y += random.randint(0,1)*2-1
                    if item_y < 1:
                        item_y += 2
                    if item_y > (room_height - 2):
                        item_y -= 2
                    if item_x < 1:
                        item_x += 2
                    if item_x > (room_width - 2):
                        item_x -= 2
                    if abs(item_y - player_y) <= 3 and abs(item_x - player_x) <= 3:
                        item_x += (random.randint(0,1)*2-1) * 3
                        item_y += (random.randint(0,1)*2-1) * 3
                grid_array[abs(item_y)][abs(item_x)] = "?"
                for y in range(len(item_stats)):
                    if y == 8:
                        info_array[x+amount_of_enemies+1][y+1] = item_x
                    elif y == 9:
                        info_array[x+amount_of_enemies+1][y+1] = item_y
                    else:
                        info_array[x+amount_of_enemies+1][y+1] = item_stats[y]
            #Now let's repeat it all for the door spawn except make that much farther away
            else:
                item_stats = enemy_dict["<"]
                item_y = random.randint(0,room_height-1)
                item_x = random.randint(0,room_width-1)
                #I think we want to spawn items with the same rules as enemies
                #10 spaces around the player on all directions nothing can init spawn
                if abs(item_y - player_y) <= 10 and abs(item_x - player_x) <= 10:
                    item_x += (random.randint(0,1)*2-1) * 3
                    item_y += (random.randint(0,1)*2-1) * 3
                while grid_array[item_y][item_x] != " ":
                    item_x += random.randint(0,1)*2-1
                    item_y += random.randint(0,1)*2-1
                    if item_y < 1:
                        item_y += 2
                    if item_y > (room_height - 2):
                        item_y -= 2
                    if item_x < 1:
                        item_x += 2
                    if item_x > (room_width - 2):
                        item_x -= 2
                    if abs(item_y - player_y) <= 10 and abs(item_x - player_x) <= 10:
                        item_x += (random.randint(0,1)*2-1) * 10
                        item_y += (random.randint(0,1)*2-1) * 10
                grid_array[abs(item_y)][abs(item_x)] = "<"
                for y in range(len(item_stats)):
                    if y == 8:
                        info_array[x+amount_of_enemies+1][y+1] = item_x
                    elif y == 9:
                        info_array[x+amount_of_enemies+1][y+1] = item_y
                    else:
                        info_array[x+amount_of_enemies+1][y+1] = item_stats[y]

        
        #Lastly let's create the game stats
        await game_info.save_game_stats(raw_data, info_array)

        #Now lets open a txt doc and write this shit
        numpy.savetxt(file_name, grid_array, fmt='%s')
        return False
    except:
        return True

PIL_GRAYSCALE = 'L'
PIL_WIDTH_INDEX = 0
PIL_HEIGHT_INDEX = 1
COMMON_MONO_FONT_FILENAMES = [
    'DejaVuSansMono.ttf',  # Linux
    'Consolas Mono.ttf',   # MacOS, I think
    'Consola.ttf',         # Windows, I think
]


async def save_mini_map(raw_input):
    game_file = "./player_files/active_" + str(raw_input.author.id) + ".txt"
    image = await textfile_to_image(game_file)
    image.show()
    image.save('./game_screens/map.png')


async def textfile_to_image(textfile_path):
    """Convert text file to a grayscale image.

    arguments:
    textfile_path - the content of this file will be converted to an image
    font_path - path to a font file (for example impact.ttf)
    """
    # parse the file into lines stripped of whitespace on the right side
    with open(textfile_path) as f:
        lines = tuple(line.rstrip() for line in f.readlines())

    # choose a font (you can see more detail in the linked library on github)
    font = None
    large_font = 20  # get better resolution with larger size
    for font_filename in COMMON_MONO_FONT_FILENAMES:
        try:
            font = ImageFont.truetype(font_filename, size=large_font)
            print(f'Using font "{font_filename}".')
            break
        except IOError:
            print(f'Could not load font "{font_filename}".')
    if font is None:
        font = ImageFont.load_default()
        print('Using default font.')

    # make a sufficiently sized background image based on the combination of font and lines
    font_points_to_pixels = lambda pt: round(pt * 96.0 / 72)
    margin_pixels = 20

    # height of the background image
    tallest_line = max(lines, key=lambda line: font.getsize(line)[PIL_HEIGHT_INDEX])
    max_line_height = font_points_to_pixels(font.getsize(tallest_line)[PIL_HEIGHT_INDEX])
    realistic_line_height = max_line_height * 0.8  # apparently it measures a lot of space above visible content
    image_height = int(ceil(realistic_line_height * len(lines) + 2 * margin_pixels))

    # width of the background image
    widest_line = max(lines, key=lambda s: font.getsize(s)[PIL_WIDTH_INDEX])
    max_line_width = font_points_to_pixels(font.getsize(widest_line)[PIL_WIDTH_INDEX])
    image_width = int(ceil(max_line_width + (2 * margin_pixels)))

    # draw the background
    background_color = 255  # white
    image = Image.new(PIL_GRAYSCALE, (image_width, image_height), color=background_color)
    draw = ImageDraw.Draw(image)

    # draw each line of text
    font_color = 0  # black
    horizontal_position = margin_pixels
    for i, line in enumerate(lines):
        vertical_position = int(round(margin_pixels + (i * realistic_line_height)))
        draw.text((horizontal_position, vertical_position), line, fill=font_color, font=font)

    return image
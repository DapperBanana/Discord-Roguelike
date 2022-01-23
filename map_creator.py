import os
import os.path
import os
import glob
import time
import random
import numpy
import game_info
from discord.ext import commands

async def generate_map(raw_data):
    #Definitions
    file_name = "active_" + str(raw_data.author.id) + ".txt"
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
        "m" : ["m", 1, 2, 0, 1, 0, -1, -1, -1, 4, 0],
        "b" : ["b", 2, 2, 0, 1, 0, -1, -1, -1, 4, 0],
        "s" : ["s", 3, 2, 1, 1, 0, -1, -1, -1, 4, 0],
        "p" : ["p", 2, 2, 1, 1, 0, -1, -1, -1, 2, 0],
        "w" : ["w", 9, 9, 9, 9, 0, -1, -1, -1, 0, 0], # Need
        "S" : ["S", 9, 9, 9, 9, 0, -1, -1, -1, 0, 0], # to
        "I" : ["I", 9, 9, 9, 9, 0, -1, -1, -1, 0, 0], # work
        "W" : ["W", 9, 9, 9, 9, 0, -1, -1, -1, 0, 0], # on
        "!" : ["!", 9, 9, 9, 9, 0, -1, -1, -1, 0, 0], # these
        "?" : ["?", 0, 0, 0, 0, 2, -1, -1, -1, 0, 0],
        "<" : ["<", 0, 0, 0, 0, 1, -1, -1, -1, 0, 0]
    }
    enemy_list = [
        "m",
        "b",
        "s",
        "p"
    ]
    level = 1
    amount_of_enemies = level * random.randint(1,5)
    amount_of_items = level * random.randint(1,2) #Items spawns are going to be based on the level you're on, and there'll only be one door per level
    player_info = ["&", 3, 10, 0, 1, 0, player_x, player_y, -1, -1, 0]
    info_array = [[void for i in range(len(player_info))] for j in range(amount_of_enemies + 1)]
    for x in range(len(player_info)):
        info_array[0][x] = player_info[x]
    for x in range(amount_of_enemies):
        enemy_val = random.randint(0, len(enemy_list)-1)
        enemy_character = enemy_list[enemy_val]
        enemy_stats = enemy_dict[enemy_character]
        enemy_y = random.randint(0,room_height-1)
        enemy_x = random.randint(0,room_width-1)
        if abs(enemy_y - player_y) <= 3 and abs(player_x - 20) <= 3:
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
            if y == 6:
                info_array[x+1][y] = enemy_x
            elif y == 7:
                info_array[x+1][y] = enemy_y
            elif y == 8:
                next_direction = random.randint(0,3)
                info_array[x+1][y] = next_direction
            else:
                info_array[x+1][y] = enemy_stats[y]
    for x in range(amount_of_items):
        #First value is going to be the door and then we'll spawn in the items
        if x > 0:
            item_stats = enemy_dict["?"]
            item_y = random.randint(0,room_height-1)
            item_x = random.randint(0,room_width-1)
            #I think we want to spawn items with the same rules as enemies
            #3 spaces around the player on all directions nothing can init spawn
            if abs(item_y - player_y) <= 3 and abs(item_x - 20) <= 3:
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
                if abs(item_y - player_y) <= 3 and abs(item_x - player_x) <= 3:
                    item_x += (random.randint(0,1)*2-1) * 3
                    item_y += (random.randint(0,1)*2-1) * 3
            grid_array[abs(item_y)][abs(item_x)] = "?"
            for y in range(len(item_stats)):
                if y == 6:
                    info_array[x+amount_of_enemies][y] = item_x
                elif y == 7:
                    info_array[x+amount_of_enemies][y] = item_y
                else:
                    info_array[x+amount_of_enemies][y] = item_stats[y]
        #Now let's repeat it all for the door spawn except make that much farther away
        else:
            item_stats = enemy_dict["<"]
            item_y = random.randint(0,room_height-1)
            item_x = random.randint(0,room_width-1)
            #I think we want to spawn items with the same rules as enemies
            #10 spaces around the player on all directions nothing can init spawn
            if abs(item_y - player_y) <= 10 and abs(item_x - 20) <= 10:
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
                if y == 6:
                    info_array[x+amount_of_enemies][y] = item_x
                elif y == 7:
                    info_array[x+amount_of_enemies][y] = item_y
                else:
                    info_array[x+amount_of_enemies][y] = item_stats[y]

    
    #Lastly let's create the game stats
    await game_info.save_game_stats(raw_data, info_array)

    #Now lets open a txt doc and write this shit
    numpy.savetxt(file_name, grid_array, fmt='%s')

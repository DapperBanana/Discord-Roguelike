import os
import os.path
import os
import glob
import time
import random
import numpy
from discord.ext import commands

#enemy_list = {
#    "m" : "12010",
#    "b" : "22010",
#    "s" : "32110",
#    "p" : "22110",
#    "w" : "45110",
#    "S" : "99990",
#    "I" : "99990",
#    "W" : "99990",
#    "!" : "99990",
#    "?" : "00002",
#    "<" : "00003"
#}

#stats_reader = {
#    1 : "strength",
#    2 : "health",
#    3 : "mana",
#    4 : "level",
#    5 : "item"
#}

async def generate_map(file_name):
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
    enemy_list = {
        "m",
        "b",
        "s",
        "p"
    }
    randchoice = {
        -1,
        1
    }
    level = 1
    amount_of_enemies = level * random.randint(1,5)
    for x in range(amount_of_enemies):
        type_of_enemy = random.randint(0,3)
        enemy_y = random.randint(0,room_height-1)
        enemy_x = random.randint(0,room_width-1)
        if abs(enemy_y - player_y) <= 3 and abs(enemy_x - player_x) <= 3:
            val = random.randint(0,1)
            if val == 0:
                val -= 1
            enemy_x += val * 3
            enemy_y += val * 3
        while grid_array[enemy_y][enemy_x] != " ":
            val = random.randint(0,1)
            if val == 0:
                val -= 1
            enemy_x += val
            enemy_y += val
            if abs(enemy_y - player_y) <= 3 and abs(enemy_x - player_x) <= 3:
                val = random.randint(0,1)
                if val == 0:
                    val -= 1
                enemy_x += val * 3
                enemy_y += val * 3
        grid_array[enemy_y][enemy_x] = enemy_list[type_of_enemy]

    #Now lets open a txt doc and write this shit
    numpy.savetxt(file_name, grid_array, fmt='%s')

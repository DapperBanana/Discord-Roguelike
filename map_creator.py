import os
import os.path
import os
import glob
import time
import random
import numpy
from discord.ext import commands


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
    #Now lets open a txt doc and write this shit
    numpy.savetxt(file_name, grid_array, fmt='%s')
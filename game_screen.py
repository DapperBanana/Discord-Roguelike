import os
import os.path
import os
import glob
import time
import random
import numpy
from discord.ext import commands

#__________.__                                    .__               
#\______   \  | _____  ___.__. ___________  ___  _|__| ______  _  __
# |     ___/  | \__  \<   |  |/ __ \_  __ \ \  \/ /  |/ __ \ \/ \/ /
# |    |   |  |__/ __ \\___  \  ___/|  | \/  \   /|  \  ___/\     / 
# |____|   |____(____  / ____|\___  >__|      \_/ |__|\___  >\/\_/  
#                    \/\/         \/                      \/   

async def resolve_screen(raw_input):
    file_name = raw_input.author.id
    #First find the player on the map
    with open("active_" + str(file_name) + ".txt") as f:
        input_grid = f.readlines()
    input_grid = [row.rstrip('\n') for row in input_grid]
    player_x = 0
    player_y = 0
    room_width = len(input_grid)
    room_height = int((len(input_grid[0]) + 1) / 2)
    #Now that we have the grid let's remove the whitespaces
    void = "-"
    grid_array = [[void for i in range(room_height)] for j in range(room_width)]
    for y in range(0,len(input_grid)-1):
        for x in range(0,len(input_grid[0])-1):
            if x % 2 == 0:
                grid_array[y][int(x/2)] = input_grid[y][x]
    #Lastly let's find the player x and y
    for y in range(0,len(grid_array)-1):
        for x in range(0,len(grid_array[0])-1):
            if grid_array[y][x] == "&":
                player_x = x
                player_y = y


    #Next lets grab what the player can see (this is multiplied by 2, this is + AND - player x and same with y)
    player_view_x,player_view_y = (5, 5)
    #And lastly create the viewable map
    viewable_grid = [[0 for x in range(player_view_y*2+1)] for y in range(player_view_x*2+1)]

    #Grab the north right coordinates and the south left coordinates to box the user in
    north_left_x = (player_x - player_view_x)
    north_left_y = (player_y - player_view_y)
    south_right_x = (player_x + player_view_x)
    south_right_y = (player_y + player_view_y)

    #Create the grid constraints
    if north_left_x < 0:
        #too far to the left
        viewable_grid_x_start = 0
    elif south_right_x >= room_width:
        #too far to the right
        viewable_grid_x_start = north_left_x - (south_right_x - (room_width - 1))
    else:
        #within bounds
        viewable_grid_x_start = north_left_x

    if north_left_y < 0:
        #too far up
        viewable_grid_y_start = 0
    elif south_right_y >= room_height:
        #too far down
        viewable_grid_y_start = north_left_y - (south_right_y - (room_height - 1))
    else:
        #within bounds
        viewable_grid_y_start = north_left_y

    for y in range(player_view_x*2+1):
        for x in range(player_view_x*2+1):
            viewable_grid[y][x] = grid_array[y + viewable_grid_y_start][x + viewable_grid_x_start]

    #Now that we have the viewable area, we want to go and place everything onto the actual game screen
    blank_space = " "
    game_screen_width = 42
    game_screen_height = 16
    #Next let's set up the complete game screen
    game_screen = [[blank_space for i in range(game_screen_width)] for j in range(game_screen_height)]
    stats_grid = [[' ',' ',' ',' ',' ',"S", "t", "a", "t", "s"],
                [' ',' ',' ',' ',' ',"-","-","-","-","-"],
                ['H','e','a','l','t','h',' ',':',' '],
                ['M','a','n','a',' ',' ',' ',':',' '],
                ['A','r','m','o','u','r',' ',':',' '],
                ['W','e','a','p','o','n',' ',':',' '],
                ['A','t','t','a','c','k',' ',':',' '],
                ['E','v','a','d','e',' ',' ',':',' '],
                [' ']]
    level_strings = [["M","o","u","n","t"," ","P","a",'r','t','h','i','l',' ','C','a','t','a','c','o','m','b','s'],
                    [' ',' ',' ',' ',' ',' ',' ',' ','L','e','v','e','l',' ','1']]
    for y in range(len(game_screen)):
        for x in range(len(game_screen[y])):
            #First lets print the stats on the side and then figure the if statement out for the viewable screen
            if y < len(stats_grid) and x >= 17:
                if (x - 17)  < len(stats_grid[y]):
                    game_screen[y][x] = stats_grid[y][x-17]
            elif y >=14 and x >= 2:
                if (x - 2) < len(level_strings[y-14]):
                    game_screen[y][x] = level_strings[y-14][x-2]
            #Need to set up the confines on where the viewable screen can print
            elif y >= 2 and y <= 12 and x >= 3 and x <= 13:
                game_screen[y][x] = viewable_grid[y-2][x-3]

    numpy.savetxt("current_view.txt", game_screen, fmt='%s')
    f = open("current_view.txt", 'r')
    await raw_input.channel.send("```" + f.read() + "```") 

    return   
    

async def print_credits(raw_data, skip_bool):
    total_credits = 10
    file_name = "credits_" + str(raw_data.author.id) + ".txt"
    tmp_screen_val = numpy.loadtxt(file_name).reshape(1)
    screen_val = int(tmp_screen_val[0])
    if not skip_bool:
        if screen_val < 10:
            credits_screen = "start_screen_" + str(screen_val) + ".txt"
            f = open(credits_screen, 'r')
            await raw_data.channel.send("```" + f.read() + "```")
            await raw_data.channel.send("Page " + str(screen_val) + "/10      please go to the *next* page or *skip*")
            save_val = [screen_val + 1]
            numpy.savetxt(file_name, save_val)
        else:
            credits_screen = "start_screen_" + str(screen_val) + ".txt"
            f = open(credits_screen, 'r')
            await raw_data.channel.send("```" + f.read() + "```")
            await raw_data.channel.send("Page " + str(screen_val) + "/10")
            await raw_data.channel.send("Now brave knight you must *enter* the catacombs!")
            #We want to delete the credits page
            os.remove(file_name)

    else:
        for x in range(screen_val, total_credits+1):
            credits_screen = "start_screen_" + str(x) + ".txt"
            f = open(credits_screen, 'r')
            await raw_data.channel.send("```" + f.read() + "```")
            await raw_data.channel.send("Page " + str(x) + "/10")
        await raw_data.channel.send("Now brave knight you must *enter* the catacombs!")
        #Lastly we need to delete the credits page
        os.remove(file_name)
    
    return

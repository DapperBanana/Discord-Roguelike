import os
import os.path
import os
import glob
import time
import random
import numpy
import discord
from discord.ext import commands

#
#__________                    .__                  _________                                   
#\______   \ ____   __________ |  |___  __ ____    /   _____/ ___________   ____   ____   ____  
# |       _// __ \ /  ___/  _ \|  |\  \/ // __ \   \_____  \_/ ___\_  __ \_/ __ \_/ __ \ /    \ 
# |    |   \  ___/ \___ (  <_> )  |_\   /\  ___/   /        \  \___|  | \/\  ___/\  ___/|   |  \
# |____|_  /\___  >____  >____/|____/\_/  \___  > /_______  /\___  >__|    \___  >\___  >___|  /
#        \/     \/     \/                     \/          \/     \/            \/     \/     \/ 
#

async def resolve_screen(raw_input):
    file_name = raw_input.author.id
    #First find the player on the map
    with open("./player_files/active_" + str(file_name) + ".txt") as f:
        input_grid = f.readlines()
    input_grid = [row.rstrip('\n') for row in input_grid]

    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    character_level = int(info_array[0][5])

    player_x = 0
    player_y = 0
    room_height = len(input_grid)
    room_width = int((len(input_grid[0]) + 1) / 2)
    #Now that we have the grid let's remove the whitespaces
    void = "-"
    grid_array = [[void for i in range(room_width)] for j in range(room_height)]
    for y in range(0,room_height):
        for x in range(0,room_width):
            grid_array[y][x] = input_grid[y][int(x * 2)]
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


    #Let's find unique characters in viewable grid

    #Now that we have the viewable area, we want to go and place everything onto the actual game screen
    level_val = character_level
    blank_space = " "
    game_screen_width = 42
    game_screen_height = 17
    #Next let's set up the complete game screen
    game_screen = [[blank_space for i in range(game_screen_width)] for j in range(game_screen_height)]
    level_strings = [["M","o","u","n","t"," ","P","a",'r','t','h','i','l'],
                    [' ',' ','C','a','t','a','c','o','m','b','s'],
                    [' ',' ',' ','L','e','v','e','l',' ',level_val]]
    #lets get the stats strings ready
    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    for row in range(len(info_array)):
        if str(info_array[row][1]) == "<":
            score_row = row
    character_level = int(info_array[0][5])
    health = str(info_array[0][3])
    mana = str(info_array[0][4])
    armour = str(info_array[0][7])
    weapon = str(info_array[0][8])
    attack = str(info_array[0][2])
    enemies_killed_score = int(info_array[score_row][2])
    items_gathered_score = int(info_array[score_row][3])
    levels_cleared_score = (character_level - 1) * 100
    armor_bonuses_score = int(info_array[score_row][4])
    weapon_bonuses_score = int(weapon) - 1
    total_score = enemies_killed_score + items_gathered_score + levels_cleared_score + armor_bonuses_score + weapon_bonuses_score
    stats_grid = [['          Stats',' '],
                ['          -----',' '],
                ['Health      :',health],
                ['Attack      :',attack],
                ['Mana        :',mana],
                ['Armour      :',armour],
                ['Weapon      :',weapon],
                ['Total Score :',total_score]]
    for y in range(len(game_screen)):
        for x in range(len(game_screen[y])):
            #First lets print the stats on the side and then figure the if statement out for the viewable screen
            if y < len(stats_grid) and x >= 13:
                if (x - 13)  < len(stats_grid[y]):
                    game_screen[y][x] = stats_grid[y][x-13]
            elif y >=14 and x >= 3:
                if (x - 3) < len(level_strings[y-14]):
                    game_screen[y][x] = level_strings[y-14][x-3]
            #Need to set up the confines on where the viewable screen can print
            elif y >= 2 and y <= 12 and x >= 1 and x <= 11:
                game_screen[y][x] = viewable_grid[y-2][x-1]

    numpy.savetxt("./player_files/current_view.txt", game_screen, fmt='%s')
    f = open("./player_files/current_view.txt", 'r')
    await raw_input.channel.send("```" + f.read() + "```") 

    return   
#
#__________        .__        __    _________                    .___.__  __          
#\______   \_______|__| _____/  |_  \_   ___ \_______   ____   __| _/|__|/  |_  ______
# |     ___/\_  __ \  |/    \   __\ /    \  \/\_  __ \_/ __ \ / __ | |  \   __\/  ___/
# |    |     |  | \/  |   |  \  |   \     \____|  | \/\  ___// /_/ | |  ||  |  \___ \ 
# |____|     |__|  |__|___|  /__|    \______  /|__|    \___  >____ | |__||__| /____  >
#                          \/               \/             \/     \/               \/ 
#     

async def print_credits(raw_data, skip_bool, client):
    total_credits = 10
    file_name = "./player_files/credits_" + str(raw_data.author.id) + ".txt"
    tmp_screen_val = numpy.loadtxt(file_name).reshape(1)
    screen_val = int(tmp_screen_val[0])
    if not skip_bool:
        if screen_val < 10:
            credits_screen = "./intro/start_screen_" + str(screen_val) + ".txt"
            f = open(credits_screen, 'r')
            await raw_data.channel.send("```" + f.read() + "```")
            await raw_data.channel.send("Page " + str(screen_val) + "/10      please go to the *next* page or *skip*")
            save_val = [screen_val + 1]
            numpy.savetxt(file_name, save_val)
        else:
            credits_screen = "./intro/start_screen_" + str(screen_val) + ".txt"
            f = open(credits_screen, 'r')
            await raw_data.channel.send("```" + f.read() + "```")
            await raw_data.channel.send("Page " + str(screen_val) + "/10")
            await raw_data.channel.send("Now brave knight you must *enter* the catacombs!")
            #We want to delete the credits page
            os.remove(file_name)
            voice = discord.utils.get(client.voice_clients, guild=raw_data.guild)
            voice.stop()
            music_val = random.randint(1,15)
            dungeon_song = "./music/dungeon_" + str(music_val) + ".mp3"
            voice.play(discord.FFmpegPCMAudio(dungeon_song))


    else:
        for x in range(screen_val, total_credits+1):
            credits_screen = "./intro/start_screen_" + str(x) + ".txt"
            f = open(credits_screen, 'r')
            await raw_data.channel.send("```" + f.read() + "```")
            await raw_data.channel.send("Page " + str(x) + "/10")
        await raw_data.channel.send("Now brave knight you must *enter* the catacombs!")
        #Lastly we need to delete the credits page
        os.remove(file_name)
        voice = discord.utils.get(client.voice_clients, guild=raw_data.guild)
        voice.stop()
        music_val = random.randint(1,15)
        dungeon_song = "./music/dungeon_" + str(music_val) + ".mp3"
        voice.play(discord.FFmpegPCMAudio(dungeon_song))
    
    return

#
#__________                    .__                __________         __    __  .__             _________                                   
#\______   \ ____   __________ |  |___  __ ____   \______   \_____ _/  |__/  |_|  |   ____    /   _____/ ___________   ____   ____   ____  
# |       _// __ \ /  ___/  _ \|  |\  \/ // __ \   |    |  _/\__  \\   __\   __\  | _/ __ \   \_____  \_/ ___\_  __ \_/ __ \_/ __ \ /    \ 
# |    |   \  ___/ \___ (  <_> )  |_\   /\  ___/   |    |   \ / __ \|  |  |  | |  |_\  ___/   /        \  \___|  | \/\  ___/\  ___/|   |  \
# |____|_  /\___  >____  >____/|____/\_/  \___  >  |______  /(____  /__|  |__| |____/\___  > /_______  /\___  >__|    \___  >\___  >___|  /
#        \/     \/     \/                     \/          \/      \/                     \/          \/     \/            \/     \/     \/ 
#
enemies = {
    "m" : "mouse",
    "b" : "bat",
    "f" : "frog",
    "s" : "spider",
    "w" : "wolf",
    "S" : "skeleton",
    "I" : "imp",
    "W" : "wizard",
    "!" : "boss"
}
enemy_grid_lengths = {
    "m" : 9,
    "b" : 5,
    "f" : 7,
    "s" : 5,
    "w" : 15,
    "S" : 15,
    "I" : 10,
    "W" : 14,
    "!" : 18
}
async def resolve_battle_screen(raw_input):

    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    #load in old info
    for row in range(len(info_array)):
        if row > 0 and int(info_array[row][13]) == 1:
            entity_val = int(info_array[row][0])
            entity_char = info_array[row][1]
    fname = "./enemies/" + str(enemies[entity_char]) + ".txt"
    with open(fname) as f:
        enemy_grid = f.readlines()
    enemy_grid = [row.rstrip('\n') for row in enemy_grid]

    #Now that we have the viewable area, we want to go and place everything onto the actual game screen
    level_val = 1
    blank_space = " "
    
    level_strings = [enemies[entity_char]]
    #lets get the stats strings ready
    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    health = str(info_array[0][3])
    mana = str(info_array[0][4])
    armour = str(info_array[0][7])
    weapon = str(info_array[0][8])
    attack = str(info_array[0][2])
    evade =  str(info_array[0][11])+ "%"
    stats_grid = [['Player Stats',' '],
                ['------------',' '],
                ['Health :',health],
                ['Attack :',attack],
                ['Mana   :',mana],
                ['Dodge  :',evade],
                ['Armour :',armour],
                ['Weapon :',weapon]]
    game_screen_width = 35
    game_screen_height = len(enemy_grid)
    if len(stats_grid) > len(enemy_grid):
        game_screen_height = len(stats_grid)
    #Next let's set up the complete game screen
    game_screen = [[blank_space for i in range(game_screen_width)] for j in range(game_screen_height)]
    for y in range(len(game_screen)):
        for x in range(len(game_screen[y])):
            #First lets print the stats on the side and then figure the if statement out for the viewable screen
            if y < len(stats_grid) and x >= 30:
                if (x - 30)  < len(stats_grid[y]):
                    game_screen[y][x] = stats_grid[y][x-30]
            elif y < len(enemy_grid):
                if x < len(enemy_grid[y]):
                    game_screen[y][x] = enemy_grid[y][x]

    numpy.savetxt("./player_files/current_view.txt", game_screen, fmt='%s', delimiter='')
    f = open("./player_files/current_view.txt", 'r')
    await raw_input.channel.send("```" + f.read() + "```")
    #test output

    return 

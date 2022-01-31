import re
import os
import os.path
import os
import glob
import time
import numpy
import game_screen
import game_info
import random
import discord
from map_creator import generate_map
from game_screen import resolve_screen
from discord.ext import commands

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# __   __  _______  ______    ___   _______  _______  ___      _______    ______   _______  _______  ___      _______  ______    _______  _______  ___   _______  __    _ 
#|  | |  ||   _   ||    _ |  |   | |   _   ||  _    ||   |    |       |  |      | |       ||       ||   |    |   _   ||    _ |  |   _   ||       ||   | |       ||  |  | |
#|  |_|  ||  |_|  ||   | ||  |   | |  |_|  || |_|   ||   |    |    ___|  |  _    ||    ___||       ||   |    |  |_|  ||   | ||  |  |_|  ||_     _||   | |   _   ||   |_| |
#|       ||       ||   |_||_ |   | |       ||       ||   |    |   |___   | | |   ||   |___ |       ||   |    |       ||   |_||_ |       |  |   |  |   | |  | |  ||       |
#|       ||       ||    __  ||   | |       ||  _   | |   |___ |    ___|  | |_|   ||    ___||      _||   |___ |       ||    __  ||       |  |   |  |   | |  |_|  ||  _    |
# |     | |   _   ||   |  | ||   | |   _   || |_|   ||       ||   |___   |       ||   |___ |     |_ |       ||   _   ||   |  | ||   _   |  |   |  |   | |       || | |   |
#  |___|  |__| |__||___|  |_||___| |__| |__||_______||_______||_______|  |______| |_______||_______||_______||__| |__||___|  |_||__| |__|  |___|  |___| |_______||_|  |__|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

defaultval = 10000
monster_gallery = [
                "m",
                "b",
                "f",
                "p"]
battle_commands = ["slash",
                "cast",
                "kill",
                "actions",
                "fireball"]
active_command_list = ["logout",
                "login",
                "end mission",
                "exit",
                "pause",
                "print",
                "enter",
                "help"]
starting_command_list = [  "login",
                    "continue",
                    "new game",
                    "test",
                    "help"]
movement_list = ["n",
                "e",
                "s",
                "w",
                "north",
                "east",
                "south",
                "west",
                "up",
                "down"]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  __   __  _______  _______  ___   _          __   __  _______  _______  ______            ___   ______  
#|       ||  | |  ||       ||       ||   | | |        |  | |  ||       ||       ||    _ |          |   | |      | 
#|       ||  |_|  ||    ___||       ||   |_| |        |  | |  ||  _____||    ___||   | ||          |   | |  _    |
#|       ||       ||   |___ |       ||      _|        |  |_|  || |_____ |   |___ |   |_||_         |   | | | |   |
#|      _||       ||    ___||      _||     |_         |       ||_____  ||    ___||    __  |        |   | | |_|   |
#|     |_ |   _   ||   |___ |     |_ |    _  | _____  |       | _____| ||   |___ |   |  | | _____  |   | |       |
#|_______||__| |__||_______||_______||___| |_||_____| |_______||_______||_______||___|  |_||_____| |___| |______| 
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def check_user_id(user_id):
    #Variable Setup
    temp = "./player_files/active_" + str(user_id) + ".txt"
    active = "na"
    exists = "na"
    active_file = False
    active_credits = False
    active_battle = False
    #Check for a an active file recorded for this person
    for name in glob.glob('./player_files/active_*.txt'):
        #If any name exists that means there is an active file
        active_file = True
        if name == temp:
            #This means that the person typing is the active user, and a file exists for them
            active = True
            exists = True
            if os.path.isfile('./player_files/credits_' + str(user_id) + ".txt"):
                active_credits = True
            if os.path.isfile('./player_files/battle_' + str(user_id) + ".txt"):
                active_battle = True
            ret_list = [active, exists, active_file, active_credits, active_battle]
            return ret_list
            #There shouldn't be any more active files than 1, but just in case we're nesting a return into here (That would be a bug for future me to figure out))
    
    active = False
    x = "./player_files/" + str(user_id) + ".txt"
    #So now we know that this user is not the one actively playing we need to determine whether any files exist under their name
    if os.path.isfile(x):
        exists = True
    else:
        exists = False

    ret_list = [active, exists, active_file, active_credits, active_battle]
    return ret_list

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  __    _  _______  ___   __    _  _______ 
#|       ||  |  | ||       ||   | |  |  | ||       |
#|    ___||   |_| ||    ___||   | |   |_| ||    ___|
#|   |___ |       ||   | __ |   | |       ||   |___ 
#|    ___||  _    ||   ||  ||   | |  _    ||    ___|
#|   |___ | | |   ||   |_| ||   | | | |   ||   |___ 
#|_______||_|  |__||_______||___| |_|  |__||_______|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def engine(text_input, user_id_info, client):

    is_active_user = user_id_info[0]
    is_user_alive = user_id_info[1]
    is_active_file = user_id_info[2]
    is_credits = user_id_info[3]
    is_battle = user_id_info[4]
    username = text_input.author.name

    if not is_active_user:
        if is_active_file:
            #there's a game going on, and you're not a part of it
            await text_input.channel.send("Unfortunately " + username + ", you are not the current player. Please wait until the current game is finished/paused.")
            return
        else:
            if str(text_input.content).lower() == "help":
                f = open("./game_screens/help_screen.txt", 'r')
                await text_input.channel.send("```" + f.read() + "```")
            #Deal with start commands first
            for command in starting_command_list:
                if command == str(text_input.content).lower():
                    await starting_commands(text_input, user_id_info, client)
                    return

            #After start commands we want to ask the basic questions
            await text_input.channel.send("Currently there are no active games going on right now.")
            

            if is_user_alive:
                #There's no game going on right now, but you have a save file
                await text_input.channel.send("It looks as though you have a savefile " + username + ", would you like to *continue*?")
                return

            else:
                #There's no game going on right now and you don't have a save file
                await text_input.channel.send(username + ", would you like to start a *new game*?")
                return

    if is_active_user:
        if not is_credits:
            if not is_battle:
                if str(text_input.content).lower() == "help":
                    f = open("./game_screens/help_screen.txt", 'r')
                    await text_input.channel.send("```" + f.read() + "```")
                #instead of looking through commands here, we're going to use an input parser, find is_command, is_movement, iteration, movement direction
                is_command, is_movement, iteration, mov_dir, command = await input_parse(text_input, client)
                if is_command:
                    if is_movement:
                        #Haven't decided whether or not I want the player to have a log of their moves
                        #await text_input.channel.purge(limit=defaultval)
                        for x in range(iteration):
                            #I want to move the player using:
                            if await out_of_battle(text_input):
                                text = await move_player(mov_dir, str(text_input.author.id), text_input)
                                enemy = await move_enemies(text_input)
                                if enemy == "ebattle":
                                    await start_battle(enemy, text_input, client)
                                elif text == "pbattle":
                                    await start_battle(text, text_input, client)
                                else:
                                    await resolve_screen(text_input)
                                    if text != "null":
                                        await text_input.channel.send(text)
                    else:
                        await text_input.channel.send(command)
                else:
                    await text_input.channel.send("That is not a recognized command, " + username + ". Would you like some *help*, to *pause*, or even *end mission*?")
            else:
                is_battle_command = False
                for battle_command in battle_commands:
                    if str(text_input.content).lower() == battle_command:
                        is_battle_command = True
                if is_battle_command:
                    await battle_round(text_input, client)
                else:
                    await text_input.channel.send("That is not a recognized command, " + username + ". Would you like some *help*, to *pause*, or even *end mission*?")
        else:
            if str(text_input.content).lower() == "next":
                await game_screen.print_credits(text_input, False, client)
            elif str(text_input.content).lower() == "skip":
                await game_screen.print_credits(text_input, True, client)
            
        return

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  _______  _______  ______    _______  ___   __    _  _______          _______  _______  __   __  __   __  _______  __    _  ______   _______ 
#|       ||       ||   _   ||    _ |  |       ||   | |  |  | ||       |        |       ||       ||  |_|  ||  |_|  ||   _   ||  |  | ||      | |       |
#|  _____||_     _||  |_|  ||   | ||  |_     _||   | |   |_| ||    ___|        |       ||   _   ||       ||       ||  |_|  ||   |_| ||  _    ||  _____|
#| |_____   |   |  |       ||   |_||_   |   |  |   | |       ||   | __         |       ||  | |  ||       ||       ||       ||       || | |   || |_____ 
#|_____  |  |   |  |       ||    __  |  |   |  |   | |  _    ||   ||  |        |      _||  |_|  ||       ||       ||       ||  _    || |_|   ||_____  |
# _____| |  |   |  |   _   ||   |  | |  |   |  |   | | | |   ||   |_| | _____  |     |_ |       || ||_|| || ||_|| ||   _   || | |   ||       | _____| |
#|_______|  |___|  |__| |__||___|  |_|  |___|  |___| |_|  |__||_______||_____| |_______||_______||_|   |_||_|   |_||__| |__||_|  |__||______| |_______|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
async def starting_commands(text_input, user_id_info, client):

    is_active_user = user_id_info[0]
    is_user_alive = user_id_info[1]
    is_active_file = user_id_info[2]
    username = text_input.author.name
    formatted_text = str(text_input.content).lower()
    #Now we have to cycle through the commands and determine which one they chose to start with
    if formatted_text == "new game":
    #start a new campaign

        #clear all old messages
        await text_input.channel.purge(limit=defaultval)
        #create a new active campaign mission
        #here we'll generate a map
        await generate_map(text_input)

        #Now start the credits
        await text_input.channel.send("New campaign started for: " + str(username))

        #Create the Credits!
        credits_name = "./player_files/credits_" + str(text_input.author.id) + ".txt"
        x = [1]
        numpy.savetxt(credits_name, x)
        await game_screen.print_credits(text_input, False, client)
        voice_channel = discord.utils.get(text_input.guild.voice_channels, name="The Catacombs")
        await voice_channel.connect()
        voice = discord.utils.get(client.voice_clients, guild=text_input.guild)
        voice.play(discord.FFmpegPCMAudio("./music/intro.mp3"))

    elif formatted_text == "continue":
    #continue

        #Change the old file to active status
        new_name = "./player_files/active_" + str(text_input.author.id) + ".txt"
        file_name = "./player_files/" + str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.rename(file_name, new_name)
            await text_input.channel.send("Campaign has been set to active!")
            voice_channel = discord.utils.get(text_input.guild.voice_channels, name="The Catacombs")
            await voice_channel.connect()
            voice = discord.utils.get(client.voice_clients, guild=text_input.guild)
            voice.play(discord.FFmpegPCMAudio("./music/dungeon.mp3"))
            await text_input.channel.send("When you are ready feel free to *enter* the catacombs!")
        else:
            await text_input.channel.send("No such campaign exists, do you want to make a *new game*?")
    
    elif formatted_text == "test":
        await text_input.channel.send("test is working")
    elif formatted_text == "login":
        file_name = "./player_files/" + str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            await text_input.channel.send("You have a paused game, would you like to *continue*?")
        else:
            await text_input.channel.send("No such campaign exists, do you want to make a *new game*?")
    
    return 

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  ___      _______  __   __  _______  ______      __   __  _______  __   __  _______  __   __  _______  __    _  _______ 
#|       ||   |    |   _   ||  | |  ||       ||    _ |    |  |_|  ||       ||  | |  ||       ||  |_|  ||       ||  |  | ||       |
#|    _  ||   |    |  |_|  ||  |_|  ||    ___||   | ||    |       ||   _   ||  |_|  ||    ___||       ||    ___||   |_| ||_     _|
#|   |_| ||   |    |       ||       ||   |___ |   |_||_   |       ||  | |  ||       ||   |___ |       ||   |___ |       |  |   |  
#|    ___||   |___ |       ||_     _||    ___||    __  |  |       ||  |_|  ||       ||    ___||       ||    ___||  _    |  |   |  
#|   |    |       ||   _   |  |   |  |   |___ |   |  | |  | ||_|| ||       | |     | |   |___ | ||_|| ||   |___ | | |   |  |   |  
#|___|    |_______||__| |__|  |___|  |_______||___|  |_|  |_|   |_||_______|  |___|  |_______||_|   |_||_______||_|  |__|  |___|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async def move_player(direction, player_name, raw_input):
    #First find the player on the map
    with open("./player_files/active_" + player_name + ".txt") as f:
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
    #next let's move in one of the four possible directions and update the map
    encounter_char, new_x, new_y = await encounter_space(direction, player_x, player_y, raw_input)
    if encounter_char == "#":
        val = "There is a wall there!"
    else:
        in_battle = 0
        for monster in monster_gallery:
            if encounter_char == monster:
                in_battle = 1
        print("----------")
        print("updating player")
        update_info = ["1", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", new_x, new_y, "NULL", "NULL", in_battle]
        await game_info.force_update(raw_input, update_info)
        print("----------")
        #need to update the monster as well
        fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
        info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
        for row in range(len(info_array)):
            str_to_print = "player_x : " + str(new_x) + " | player_y : " + str(new_y)
            print(str_to_print)
            str_to_print = "entity_x : " + str(info_array[row][9]) + " | entity_y : " + str(info_array[row][10] )
            print(str_to_print)
            print(row)
            if row > 0:
                if (int(info_array[row][9]) == new_x) and (int(info_array[row][10]) == new_y):
                    enemy_val = info_array[row][0]
                    print("----------")
                    print("updating player")
                    update_info = [str(enemy_val), "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", in_battle]
                    await game_info.force_update(raw_input, update_info)
                    print("----------")
        #So now we have updated the game info file, and moved the player ahead
        grid_array[player_y][player_x] = " "
        grid_array[new_y][new_x] = "&"
        #save it to the active player file
        file_name = "./player_files/active_" + str(player_name) + ".txt"
        numpy.savetxt(file_name, grid_array, fmt='%s')
        if in_battle:
            val = "pbattle"
        else:
            val = "null"
        
    return val

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ___   __    _  _______  __   __  _______    _______  _______  ______    _______  _______  ______   
#|   | |  |  | ||       ||  | |  ||       |  |       ||   _   ||    _ |  |       ||       ||    _ |  
#|   | |   |_| ||    _  ||  | |  ||_     _|  |    _  ||  |_|  ||   | ||  |  _____||    ___||   | ||  
#|   | |       ||   |_| ||  |_|  |  |   |    |   |_| ||       ||   |_||_ | |_____ |   |___ |   |_||_ 
#|   | |  _    ||    ___||       |  |   |    |    ___||       ||    __  ||_____  ||    ___||    __  |
#|   | | | |   ||   |    |       |  |   |    |   |    |   _   ||   |  | | _____| ||   |___ |   |  | |
#|___| |_|  |__||___|    |_______|  |___|    |___|    |__| |__||___|  |_||_______||_______||___|  |_|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async def input_parse(raw_input, client):
    #These are the return values
    input_is_command = 0 #0 for no, 1 for yes
    input_is_movement = 0 #0 for no, 1 for yes
    iterative_value = 0 #This is how many times the character will move automatically
    movement_direction = 0 #0 is n, 1 is east, 2 is south, and 3 is west
    message_to_send = " " #This is the message that will be sent back should there be a command
    #Before we do anything lets lower the punctuation to make everything easier
    formatted_input = str(raw_input.content).lower()
    #First let's find if you're a part of the command list
    for command in active_command_list:
        if formatted_input == command:
            input_is_command = 1
            input_is_movement = 0
            #This is when we iterate through all the fucking commands
            if formatted_input == "pause":
                #clear all old messages
                await raw_input.channel.purge(limit=defaultval)
                #Change the current file to non active status
                file_name = "./player_files/active_" + str(raw_input.author.id) + ".txt"
                new_name = "./player_files/" + str(raw_input.author.id) + ".txt"
                if os.path.exists(file_name):
                    os.rename(file_name, new_name)
                    message_to_send =  "Campaign has been paused! Until next time!"
                    voice = discord.utils.get(client.voice_clients, guild=raw_input.guild)
                    voice.stop()
                    await voice.disconnect()

            elif formatted_input == "end mission":
                #clear all old messages
                await raw_input.channel.purge(limit=defaultval)
                #Delete the file
                game_file = "./player_files/active_" + str(raw_input.author.id) + ".txt"
                game_info_file = "./player_files/info_" + str(raw_input.author.id) + ".txt"
                if os.path.exists(game_file):
                    os.remove(game_file)
                    os.remove(game_info_file)
                    message_to_send = "Campaign has ended! Safe travels"
                voice = discord.utils.get(client.voice_clients, guild=raw_input.guild)
                voice.stop()
                await voice.disconnect()
            elif formatted_input == "enter":
                await resolve_screen(raw_input)
                message_to_send = "You have entered the mighty catacombs of Mount Parthil. Good luck Adventurer!"
            elif formatted_input == "wait":
                await resolve_screen(raw_input)
            elif formatted_input == "login":
                message_to_send = "You are currently playing!"
    #After we've iterated through the commands list let's now see if we're dealing with a direction/movement command
    #First we're looking for just a direction, no iteration
    for direction in movement_list:
        if formatted_input == direction:
            input_is_command = 1
            input_is_movement = 1
            iterative_value = 1
            if direction == "n" or direction == "north":
                movement_direction = 0
            elif direction == "e" or direction == "east":
                movement_direction = 1
            elif direction == "s" or direction == "south":
                movement_direction = 2
            elif direction == "w" or direction == "west":
                movement_direction = 3

    #Lastly let's RegEx this bitch and find iterative values
    if re.search("\d+[nesw]$", formatted_input):
        input_is_command = 1
        input_is_movement = 1
        x = re.search("[nesw]", formatted_input)
        char_index_val = x.span()
        direction = formatted_input[char_index_val[0]]
        x = re.split("[nesw]", formatted_input)
        iterative_value = int(x[0])
        if direction == "n":
            movement_direction = 0
        elif direction == "e":
            movement_direction = 1
        elif direction == "s":
            movement_direction = 2
        elif direction == "w":
            movement_direction = 3

    return input_is_command, input_is_movement, iterative_value, movement_direction, message_to_send

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  __    _  _______  __   __  __   __    _______  _______  _______  __   __  _______  ___   __    _  ______   ___   __    _  _______ 
#|       ||  |  | ||       ||  |_|  ||  | |  |  |       ||   _   ||       ||  | |  ||       ||   | |  |  | ||      | |   | |  |  | ||       |
#|    ___||   |_| ||    ___||       ||  |_|  |  |    _  ||  |_|  ||_     _||  |_|  ||    ___||   | |   |_| ||  _    ||   | |   |_| ||    ___|
#|   |___ |       ||   |___ |       ||       |  |   |_| ||       |  |   |  |       ||   |___ |   | |       || | |   ||   | |       ||   | __ 
#|    ___||  _    ||    ___||       ||_     _|  |    ___||       |  |   |  |       ||    ___||   | |  _    || |_|   ||   | |  _    ||   ||  |
#|   |___ | | |   ||   |___ | ||_|| |  |   |    |   |    |   _   |  |   |  |   _   ||   |    |   | | | |   ||       ||   | | | |   ||   |_| |
#|_______||_|  |__||_______||_|   |_|  |___|    |___|    |__| |__|  |___|  |__| |__||___|    |___| |_|  |__||______| |___| |_|  |__||_______|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
enemy_sight = {
    "m" : 2,
    "b" : 3,
    "f" : 2,
    "s" : 3,
    "w" : 9,
    "S" : 9,
    "I" : 9,
    "W" : 9,
    "!" : 9  
}
entity_list = ["m","b","f","s","w","S","I","W","!","<","?","#"]

async def move_enemies(raw_input):
    #First things first we want to load the map into an array
    with open("./player_files/active_" + str(raw_input.author.id) + ".txt") as f:
        input_grid = f.readlines()
        input_grid = [row.rstrip('\n') for row in input_grid]
        room_width = len(input_grid)
        room_height = int((len(input_grid[0]) + 1) / 2)
        #Now that we have the grid let's remove the whitespaces
        void = "-"
        grid_array = [[void for i in range(room_height)] for j in range(room_width)]
        for y in range(0,len(input_grid)-1):
            for x in range(0,len(input_grid[0])-1):
                if x % 2 == 0:
                    grid_array[y][int(x/2)] = input_grid[y][x]
    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    amount_of_enemies = 0
    player_x = int(info_array[0][9])
    player_y = int(info_array[0][10])
    #We know that the player character is on entity #1, we need to know how many enemies there are.
    #Luckily we know that they're sandwiched between the player and the door, so figure out where the door is, subtract 1 and that's the amount of enemies
    for row in range(len(info_array)):
        if info_array[row][1] == "<":
            amount_of_enemies = int(info_array[row][0]) - 2
    #Now that we have the amount of enemies, let's start cycling through them and updating everything.
    return_val = "null"
    for enemy in range(amount_of_enemies):
        #First lets grab the units x and y
        enemy_type = info_array[enemy + 1][1]
        #check if the enemy is dead first
        if enemy_type == "X":
            continue
        #next check if the enemy is in battle
        in_battle = info_array[enemy + 1][13]
        if int(in_battle) == 1:
            continue
        enemy_x = int(info_array[enemy + 1][9]) #we add 2 to get back to the entity number
        enemy_y = int(info_array[enemy + 1][10])
        encounter_direction = 0
        #Now lets see if the enemy is near the player
        diff_x = abs(enemy_x - player_x)
        diff_y = abs(enemy_y - player_y)
        enemy_vis_length = enemy_sight[enemy_type]
        if (diff_x <= int(enemy_vis_length)) and (diff_y <= int(enemy_vis_length)):
            #If within their sight, we want to grab which value is closest (if there is one)
            if diff_x == diff_y:
                x_or_y = random.randint(0,1)*2-1
                y = 1
                if x_or_y == y:
                    if enemy_y < player_y:
                        encounter_direction = 2
                    else:
                        encounter_direction = 0
                else:
                    if enemy_x < player_x:
                        encounter_direction = 1
                    else:
                        encounter_direction = 3
            elif diff_y < diff_x:
                if enemy_y != player_y:
                    if enemy_y < player_y:
                        encounter_direction = 2
                    else:
                        encounter_direction = 0
                else:
                    if enemy_x < player_x:
                        encounter_direction = 1
                    else:
                        encounter_direction = 3
            else:
                if enemy_x != player_x:
                    if enemy_x < player_x:
                        encounter_direction = 1
                    else:
                        encounter_direction = 3
                else:
                    if enemy_y < player_y:
                        encounter_direction = 2
                    else:
                        encounter_direction = 0
        #If we're not within sight, then we want to grab their path that they should be on
        #At the end we'll encounter the space and then move from there
        else:
            #Screw the pathing for a bit and lets just move the enemies around randomly
            encounter_direction = random.randint(0,3)
        encounter_char, new_x, new_y = await encounter_space(encounter_direction,enemy_x, enemy_y, raw_input)
        #Need to find out if the encountered area is an entity or not
        hit_entity = False
        for entity in range(len(entity_list)):
            if encounter_char == entity_list[entity]:
                hit_entity = True
        if encounter_char == "&":
            #If we've hit the player, we're gonna have to enter battle!
            #First update the info, then return the enemy battle tag
            in_battle = 1
            update_info = ["1", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", in_battle]
            await game_info.force_update(raw_input, update_info)
            update_info = [str(enemy + 2), "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", new_x, new_y, "NULL", "NULL", in_battle]
            await game_info.force_update(raw_input, update_info)
            grid_array[enemy_y][enemy_x] = " "
            file_name = "./player_files/active_" + str(raw_input.author.id) + ".txt"
            numpy.savetxt(file_name, grid_array, fmt='%s')
            return_val = "ebattle"
        elif hit_entity:
            continue
        else:
            #otherwise we hit a space and lets update the map and info with that
            update_info = [str(enemy + 2), "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", new_x, new_y, "NULL", "NULL", "NULL"]
            await game_info.force_update(raw_input, update_info)
            grid_array[enemy_y][enemy_x] = " "
            grid_array[new_y][new_x] = enemy_type
            file_name = "./player_files/active_" + str(raw_input.author.id) + ".txt"
            numpy.savetxt(file_name, grid_array, fmt='%s')
    
    return return_val



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  __    _  _______  _______  __   __  __    _  _______  _______  ______      _______  __   __  _______  _______  _______  __   __ 
#|       ||  |  | ||       ||       ||  | |  ||  |  | ||       ||       ||    _ |    |       ||  | |  ||       ||       ||       ||  |_|  |
#|    ___||   |_| ||       ||   _   ||  | |  ||   |_| ||_     _||    ___||   | ||    |  _____||  |_|  ||  _____||_     _||    ___||       |
#|   |___ |       ||       ||  | |  ||  |_|  ||       |  |   |  |   |___ |   |_||_   | |_____ |       || |_____   |   |  |   |___ |       |
#|    ___||  _    ||      _||  |_|  ||       ||  _    |  |   |  |    ___||    __  |  |_____  ||_     _||_____  |  |   |  |    ___||       |
#|   |___ | | |   ||     |_ |       ||       || | |   |  |   |  |   |___ |   |  | |   _____| |  |   |   _____| |  |   |  |   |___ | ||_|| |
#|_______||_|  |__||_______||_______||_______||_|  |__|  |___|  |_______||___|  |_|  |_______|  |___|  |_______|  |___|  |_______||_|   |_|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def encounter_space(direction, entity_x, entity_y, raw_input):
    #First things first we want to load the map into an array
    with open("./player_files/active_" + str(raw_input.author.id) + ".txt") as f:
        input_grid = f.readlines()
        input_grid = [row.rstrip('\n') for row in input_grid]
        room_width = len(input_grid)
        room_height = int((len(input_grid[0]) + 1) / 2)
        #Now that we have the grid let's remove the whitespaces
        void = "-"
        grid_array = [[void for i in range(room_height)] for j in range(room_width)]
        for y in range(0,len(input_grid)-1):
            for x in range(0,len(input_grid[0])-1):
                if x % 2 == 0:
                    grid_array[y][int(x/2)] = input_grid[y][x]
    #Next lets grab the x and y of the space that the entity is encountering
    encounter_x = entity_x
    encounter_y = entity_y
    if direction == 0:
        encounter_y -= 1
    elif direction == 1:
        encounter_x += 1
    elif direction == 2:
        encounter_y += 1
    elif direction == 3:
        encounter_x -= 1
    return_char = grid_array[encounter_y][encounter_x]
    return return_char, encounter_x, encounter_y

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  _______  _______  ______    _______    _______  _______  _______  _______  ___      _______ 
#|       ||       ||   _   ||    _ |  |       |  |  _    ||   _   ||       ||       ||   |    |       |
#|  _____||_     _||  |_|  ||   | ||  |_     _|  | |_|   ||  |_|  ||_     _||_     _||   |    |    ___|
#| |_____   |   |  |       ||   |_||_   |   |    |       ||       |  |   |    |   |  |   |    |   |___ 
#|_____  |  |   |  |       ||    __  |  |   |    |  _   | |       |  |   |    |   |  |   |___ |    ___|
# _____| |  |   |  |   _   ||   |  | |  |   |    | |_|   ||   _   |  |   |    |   |  |       ||   |___ 
#|_______|  |___|  |__| |__||___|  |_|  |___|    |_______||__| |__|  |___|    |___|  |_______||_______|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

async def start_battle(initiate, raw_input, client):
    #I'll have to use the raw input to get the x and y and of the battle through the info file
    if initiate == "pbattle":
        await raw_input.channel.send("player initiated battle")
    elif initiate == "ebattle":
        await raw_input.channel.send("enemy initiated battle")
    fname = "./player_files/battle_" + str(raw_input.author.id) + ".txt"
    x = [1]
    numpy.savetxt(fname, x)
    #find the enemy character of what you're fighting
    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    entity_val = 0
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    for row in range(len(info_array)):
        if row > 0 and int(info_array[row][13]) == 1:
            entity_val = int(info_array[row][0])
    entity_char = str(info_array[entity_val-1][1])
    fname = "./enemies/" + str(enemies[entity_char]) + ".txt"
    f = open(fname, 'r')
    await raw_input.channel.send("```" + f.read() + "```")
    voice = discord.utils.get(client.voice_clients, guild=raw_input.guild)
    voice.stop()
    voice.play(discord.FFmpegPCMAudio("./music/battle.mp3"))
    await raw_input.channel.send("Remember you can request a list of *actions* if you've forgotten your skills.")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  _______  _______  _______  ___      _______    ______    _______  __   __  __    _  ______  
#|  _    ||   _   ||       ||       ||   |    |       |  |    _ |  |       ||  | |  ||  |  | ||      | 
#| |_|   ||  |_|  ||_     _||_     _||   |    |    ___|  |   | ||  |   _   ||  | |  ||   |_| ||  _    |
#|       ||       |  |   |    |   |  |   |    |   |___   |   |_||_ |  | |  ||  |_|  ||       || | |   |
#|  _   | |       |  |   |    |   |  |   |___ |    ___|  |    __  ||  |_|  ||       ||  _    || |_|   |
#| |_|   ||   _   |  |   |    |   |  |       ||   |___   |   |  | ||       ||       || | |   ||       |
#|_______||__| |__|  |___|    |___|  |_______||_______|  |___|  |_||_______||_______||_|  |__||______| 
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
enemy_name_list = {
    "m" : "nasty mouse",
    "b" : "giant bat",
    "f" : "poisonous frog",
    "s" : "terrible spider",
    "w" : "9",
    "S" : "9",
    "I" : "9",
    "W" : "9",
    "!" : "9"
}
async def battle_round(raw_input, client):
    #This is where we'll reopen the battle file and continue
    for battle_command in battle_commands:
        if str(raw_input.content).lower() == battle_command:
            #lets first find the enemy the player has encountered
            fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
            entity_val = 0
            info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
            for row in range(len(info_array)):
                if row > 0 and int(info_array[row][13]) == 1:
                    entity_val = int(info_array[row][0])
            entity_char = str(info_array[entity_val-1][1])
            #Let's hurt the player and such
            total_player_attack = int(info_array[0][8]) + int(info_array[0][2])
            total_player_health = int(info_array[0][7]) + int(info_array[0][3])
            total_enemy_attack = int(info_array[entity_val-1][8]) + int(info_array[entity_val-1][2])
            total_enemy_health = int(info_array[entity_val-1][7]) + int(info_array[entity_val-1][3])
            output_string = "You swung your sword for " + str(total_player_attack) + " points of damage!"
            await raw_input.channel.send(output_string)
            if total_player_attack >= total_enemy_health:
                output_string = "You killed the " + enemy_name_list[entity_char] + "!"
                await raw_input.channel.send(output_string)
                #then update the info file
                in_battle = 0
                update_info = ["1", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", "NULL", in_battle]
                await game_info.force_update(raw_input, update_info)
                update_info = [str(entity_val), "X", "NULL", 0, "NULL", "NULL", "NULL", 0, "NULL", "NULL", "NULL", "NULL", "NULL", in_battle]
                await game_info.force_update(raw_input, update_info)
                fname = "./player_files/battle_" + str(raw_input.author.id) + ".txt"
                os.remove(fname)
                voice = discord.utils.get(client.voice_clients, guild=raw_input.guild)
                voice.stop()
                voice.play(discord.FFmpegPCMAudio("./music/dungeon.mp3"))
                await resolve_screen(raw_input)
            else:
                total_enemy_health -= total_player_attack
                output_string = "The " + enemy_name_list[entity_char] + " attacked you for "+ str(total_enemy_attack) + " points of damage!"
                await raw_input.channel.send(output_string)
                total_player_health -= total_enemy_attack
                if total_player_health <= 0:
                    fname = "./player_files/battle_" + str(raw_input.author.id) + ".txt"
                    os.remove(fname)
                    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
                    os.remove(fname)
                    fname = "./player_files/active_" + str(raw_input.author.id) + ".txt"
                    os.remove(fname)
                    await raw_input.channel.purge(limit=defaultval)
                    voice = discord.utils.get(client.voice_clients, guild=raw_input.guild)
                    voice.stop()
                    await voice.disconnect()
                    f = open("./game_screens/death.txt", 'r')
                    await raw_input.channel.send("```" + f.read() + "```") 
                    await raw_input.channel.send("You have died in the catacombs; Better luck next time!")
                    await raw_input.channel.send("Would you like to start a *new game*?")

                else:
                    if total_player_health <= int(info_array[0][3]):
                        new_player_health = total_player_health
                        new_player_armor = 0
                    elif total_player_health > int(info_array[0][3]):
                        new_player_health = int(info_array[0][3])
                        new_player_armor = total_player_health - int(info_array[0][3])
                    #Now the same for enemies
                    if total_enemy_health <= int(info_array[entity_val-1][3]):
                        new_enemy_health = total_enemy_health
                        new_enemy_armor = 0
                    elif total_enemy_health > int(info_array[entity_val-1][3]):
                        new_enemy_health = int(info_array[entity_val-1][3])
                        new_enemy_armor = total_enemy_health - int(info_array[entity_val-1][3])
                    #Now to save the health
                    update_info = ["1", "NULL", "NULL", new_player_health, "NULL", "NULL", "NULL", new_player_armor, "NULL", "NULL", "NULL", "NULL", "NULL", "NULL"]
                    await game_info.force_update(raw_input, update_info)
                    update_info = [str(entity_val + 1), "NULL", "NULL", new_enemy_health, "NULL", "NULL", "NULL", new_enemy_armor, "NULL", "NULL", "NULL", "NULL", "NULL", "NULL"]
                    await game_info.force_update(raw_input, update_info)

async def out_of_battle(raw_input):
    #This is where we'll reopen the battle file and continue
    out_of_battle = True
    fname = "./player_files/battle_" + str(raw_input.author.id) + ".txt"
    if os.path.isfile(fname):
                out_of_battle = False
    return out_of_battle

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                 __    _  _______  __   __  _______                 
#                |  |  | ||   _   ||  |_|  ||       |                
#                |   |_| ||  |_|  ||       ||    ___|                
#                |       ||       ||       ||   |___                 
#                |  _    ||       ||       ||    ___|                
# _____   _____  | | |   ||   _   || ||_|| ||   |___  _____   _____  
#|_____| |_____| |_|  |__||__| |__||_|   |_||_______||_____| |_____| 
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    engine()
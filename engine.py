import re
import os
import os.path
import os
import glob
import time
import numpy
import game_screen
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

defaultval = 100

active_command_list = ["logout",
                "login",
                "end mission",
                "exit",
                "pause",
                "print",
                "enter"]

starting_command_list = [  "login",
                    "continue",
                    "new game",
                    "test"
                    ]

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

starting_credits_latch = 1

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
    temp = "active_" + str(user_id) + ".txt"
    active = "na"
    exists = "na"
    active_file = False
    active_credits = False
    #Check for a an active file recorded for this person
    for name in glob.glob('active_*.txt'):
        #If any name exists that means there is an active file
        active_file = True
        if name == temp:
            #This means that the person typing is the active user, and a file exists for them
            active = True
            exists = True
            if os.path.isfile('./credits_' + str(user_id) + ".txt"):
                active_credits = True
            ret_list = [active, exists, active_file, active_credits]
            return ret_list
            #There shouldn't be any more active files than 1, but just in case we're nesting a return into here (That would be a bug for future me to figure out))
    
    active = False
    x = str(user_id) + ".txt"
    #So now we know that this user is not the one actively playing we need to determine whether any files exist under their name
    if os.path.isfile(x):
        exists = True
    else:
        exists = False

    ret_list = [active, exists, active_file, active_credits]
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

async def engine(text_input, user_id_info):

    is_active_user = user_id_info[0]
    is_user_alive = user_id_info[1]
    is_active_file = user_id_info[2]
    is_credits = user_id_info[3]
    username = text_input.author.name

    if not is_active_user:
        if is_active_file:
            #there's a game going on, and you're not a part of it
            await text_input.channel.send("Unfortunately " + username + ", you are not the current player. Please wait until the current game is finished/paused.")
            return
        else:
            if str(text_input.content).lower() == "help":
                f = open("help_screen.txt", 'r')
                await text_input.channel.send("```" + f.read() + "```")
            #Deal with start commands first
            for command in starting_command_list:
                if command == str(text_input.content).lower():
                    await starting_commands(text_input, user_id_info)
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
            if str(text_input.content).lower() == "help":
                f = open("help_screen.txt", 'r')
                await text_input.channel.send("```" + f.read() + "```")
            #instead of looking through commands here, we're going to use an input parser, find is_command, is_movement, iteration, movement direction
            is_command, is_movement, iteration, mov_dir, command = await input_parse(text_input)
            if is_command:
                if is_movement:
                    #Haven't decided whether or not I want the player to have a log of their moves
                    #await text_input.channel.purge(limit=defaultval)
                    for x in range(iteration):
                        #I want to move the player using:
                        text = await move_player(mov_dir, str(text_input.author.id), text_input)
                        await resolve_screen(text_input)
                        if text != "null":
                            await text_input.channel.send(text)

                else:
                    await text_input.channel.send(command)
            else:
                await text_input.channel.send("That is not a recognized command, " + username + ". Would you like some *help*, to *pause*, or even *end mission*?")
        else:
            if str(text_input.content).lower() == "next":
                await game_screen.print_credits(text_input, False)
            elif str(text_input.content).lower() == "skip":
                await game_screen.print_credits(text_input, True)
            
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
    
async def starting_commands(text_input, user_id_info):

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
        credits_name = "credits_" + str(text_input.author.id) + ".txt"
        x = [1]
        numpy.savetxt(credits_name, x)
        await game_screen.print_credits(text_input, False)

    elif formatted_text == "continue":
    #continue

        #Change the old file to active status
        new_name = "active_" + str(text_input.author.id) + ".txt"
        file_name = str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.rename(file_name, new_name)
            await text_input.channel.send("Campaign has been set to active!")
            await text_input.channel.send("When you are ready feel free to *enter* the catacombs!")
        else:
            await text_input.channel.send("No such campaign exists, do you want to make a *new game*?")
    
    elif formatted_text == "test":
        await text_input.channel.send("test is working")
    elif formatted_text == "login":
        file_name = str(text_input.author.id) + ".txt"
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
    with open("active_" + player_name + ".txt") as f:
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
    old_x = player_x
    old_y = player_y
    #next let's move in one of the four possible directions and update the map
    if direction == 0:
        player_y -= 1
    elif direction == 1:
        player_x += 1
    elif direction == 2:
        player_y += 1
    elif direction == 3:
        player_x -= 1
    if grid_array[player_y][player_x] == "#":
        val = "There is a wall there!"
    else:
        #update the player location in the active file
        #erase the previous location for the player
        grid_array[old_y][old_x] = " "
        grid_array[player_y][player_x] = "&"
        #save it to the active player file
        file_name = "active_" + str(player_name) + ".txt"
        numpy.savetxt(file_name, grid_array, fmt='%s')
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
async def input_parse(raw_input):
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
                file_name = "active_" + str(raw_input.author.id) + ".txt"
                new_name = str(raw_input.author.id) + ".txt"
                if os.path.exists(file_name):
                    os.rename(file_name, new_name)
                    message_to_send =  "Campaign has been paused! Until next time!"

            elif formatted_input == "end mission":
                #clear all old messages
                await raw_input.channel.purge(limit=defaultval)
                #Delete the file
                game_file = "active_" + str(raw_input.author.id) + ".txt"
                game_info_file = "info_" + str(raw_input.author.id) + ".txt"
                if os.path.exists(game_file):
                    os.remove(game_file)
                    os.remove(game_info_file)
                    message_to_send = "Campaign has ended! Safe travels"
            elif formatted_input == "enter":
                await resolve_screen(raw_input)
                message_to_send = "You have entered the mighty catacombs of Mount Parthil. Good luck Adventurer!"
            elif formatted_input == "print":
                f = open("print-me.txt", 'r')
                await raw_input.channel.send("```" + f.read() + "```") 
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


#
#
#
#
#
#
#
if __name__ == '__main__':
    engine()
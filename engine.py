import os
import os.path
import os
import glob
import time
import numpy
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

active_command_list = ["w",
                "a",
                "s",
                "d",
                "up",
                "down",
                "left",
                "right",
                "logout",
                "end mission",
                "exit",
                "pause",
                "print",
                "n",
                "e",
                "s",
                "w",
                "north",
                "east",
                "south",
                "west"]

starting_command_list = [  "login",
                    "continue",
                    "new game",
                    "test"]

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

    #Check for a an active file recorded for this person
    for name in glob.glob('active_*.txt'):
        #If any name exists that means there is an active file
        active_file = True
        if name == temp:
            #This means that the person typing is the active user, and a file exists for them
            active = True
            exists = True
            ret_list = [active, exists, active_file]
            return ret_list
            #There shouldn't be any more active files than 1, but just in case we're nesting a return into here (That would be a bug for future me to figure out))
    
    active = False
    x = str(user_id) + ".txt"
    #So now we know that this user is not the one actively playing we need to determine whether any files exist under their name
    if os.path.isfile(x):
        exists = True
    else:
        exists = False

    ret_list = [active, exists, active_file]
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
    username = text_input.author.name

    if not is_active_user:
        if is_active_file:
            #there's a game going on, and you're not a part of it
            await text_input.channel.send("Unfortunately " + username + ", you are not the current player. Please wait until the current game is finished/paused.")
            return
        else:
            #Deal with start commands first
            for command in starting_command_list:
                if command == text_input.content:
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
        for command in active_command_list:

            if str(text_input.content).find(command):
                new_text = await active_commands(text_input, user_id_info)
                if new_text == "print" or new_text == "moved":
                    await text_input.channel.purge(limit=defaultval)
                    await resolve_screen(text_input.author.id)
                    tempfilename = "test_view.txt"
                    f = open(tempfilename, 'r')
                    await text_input.channel.send("```" + f.read() + "```")
                else:
                    await text_input.channel.send(new_text)
                
                return
        #There's a game going on and you are the correct person to be typing
        await text_input.channel.send("That is not a recognized command, " + username + ". Would you like some *help*, to *pause*, or even *end mission*?")
        return

    #screen_width = 20
    #screen_height = 20

    #player_x = int(screen_width / 2)
    #player_y = int(screen_height / 2)

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

    #Now we have to cycle through the commands and determine which one they chose to start with
    if text_input.content == "new game":
    #start a new campaign

        #clear all old messages
        await text_input.channel.purge(limit=defaultval)
        #create a new active campaign mission
        file_name = "active_" + str(text_input.author.id) + ".txt"
        #here we'll generate a map
        await generate_map(file_name)

        #Now start the credits
        await text_input.channel.send("New campaign started for: " + str(username))
        await text_input.channel.send("Game will start in:")
        for x in range(5, 0, -1):        
            time.sleep(1)
            temp = str(x) + "..."
            await text_input.channel.send(temp)
        
        for x in range(1,5):
            await text_input.channel.purge(limit=defaultval)
            tempfilename = "start_screen_" + str(x) + ".txt"
            f = open(tempfilename, 'r')
            await text_input.channel.send("```" + f.read() + "```")
            time.sleep(5)

    elif text_input.content == "continue":
    #continue

        #Change the old file to active status
        new_name = "active_" + str(text_input.author.id) + ".txt"
        file_name = str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.rename(file_name, new_name)
            await text_input.channel.send("Campaign has been set to active!")
        else:
            await text_input.channel.send("No such campaign exists, do you want to make a *new campaign*?")
    
    elif text_input.content == "test":
        await text_input.channel.send("test is working")
    
    return

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  _______  _______  ___   __   __  _______    _______  _______  __   __  __   __  _______  __    _  ______   _______ 
#|   _   ||       ||       ||   | |  | |  ||       |  |       ||       ||  |_|  ||  |_|  ||   _   ||  |  | ||      | |       |
#|  |_|  ||       ||_     _||   | |  |_|  ||    ___|  |       ||   _   ||       ||       ||  |_|  ||   |_| ||  _    ||  _____|
#|       ||       |  |   |  |   | |       ||   |___   |       ||  | |  ||       ||       ||       ||       || | |   || |_____ 
#|       ||      _|  |   |  |   | |       ||    ___|  |      _||  |_|  ||       ||       ||       ||  _    || |_|   ||_____  |
#|   _   ||     |_   |   |  |   |  |     | |   |___   |     |_ |       || ||_|| || ||_|| ||   _   || | |   ||       | _____| |
#|__| |__||_______|  |___|  |___|   |___|  |_______|  |_______||_______||_|   |_||_|   |_||__| |__||_|  |__||______| |_______|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

async def active_commands(text_input, user_id_info):
    input_command = str(text_input.content).lower()
    if input_command == "pause":
        #pause your campaign

        #clear all old messages
        await text_input.channel.purge(limit=defaultval)
        #Change the current file to non active status
        file_name = "active_" + str(text_input.author.id) + ".txt"
        new_name = str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.rename(file_name, new_name)
            return "Campaign has been paused! Until next time!"

    elif input_command == "end mission":
        #end your campaign

        #clear all old messages
        await text_input.channel.purge(limit=defaultval)
        #Delete the file
        file_name = "active_" + str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.remove(file_name)
            return "Campaign has ended! Safe travels"
    
    elif input_command == "n" or input_command == "north":
        await move_player(0, str(text_input.author.id))
        return "moved"
    elif input_command == "e" or input_command == "east":
        await move_player(1, str(text_input.author.id))
        return "moved"
    elif input_command == "s" or input_command == "south":
        await move_player(2, str(text_input.author.id))
        return "moved"
    elif input_command == "w" or input_command == "west":
        await move_player(3, str(text_input.author.id))
        return "moved"
    
    else:
        return "print"

if __name__ == '__main__':
    engine()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# _______  ___      _______  __   __  _______  ______      __   __  _______  __   __  _______  __   __  _______  __    _  _______ 
#|       ||   |    |   _   ||  | |  ||       ||    _ |    |  |_|  ||       ||  | |  ||       ||  |_|  ||       ||  |  | ||       |
#|    _  ||   |    |  |_|  ||  |_|  ||    ___||   | ||    |       ||   _   ||  |_|  ||    ___||       ||    ___||   |_| ||_     _|
#|   |_| ||   |    |       ||       ||   |___ |   |_||_   |       ||  | |  ||       ||   |___ |       ||   |___ |       |  |   |  
#|    ___||   |___ |       ||_     _||    ___||    __  |  |       ||  |_|  ||       ||    ___||       ||    ___||  _    |  |   |  
#|   |    |       ||   _   |  |   |  |   |___ |   |  | |  | ||_|| ||       | |     | |   |___ | ||_|| ||   |___ | | |   |  |   |  
#|___|    |_______||__| |__|  |___|  |_______||___|  |_|  |_|   |_||_______|  |___|  |_______||_|   |_||_______||_|  |__|  |___|
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async def move_player(direction, player_name):
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
    
    #erase the previous location for the player
    grid_array[player_y][player_x] = " "
    #next let's move in one of the four possible directions and update the map
    if direction == 0:
        player_y -= 1
    elif direction == 1:
        player_x += 1
    elif direction == 2:
        player_y += 1
    elif direction == 3:
        player_x -= 1
    #update the player location in the active file
    grid_array[player_y][player_x] = "&"
    #save it to the active player file
    file_name = "active_" + str(player_name) + ".txt"
    numpy.savetxt(file_name, grid_array, fmt='%s')
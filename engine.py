import os
import os.path
import os
import glob
import time
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
                "pause"]

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
            if command == text_input.content:
                await active_commands(text_input, user_id_info)
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
        f = open(file_name, 'w+')
        f.write("campaign started")
        f.close()

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

    if text_input.content == "pause":
        #pause your campaign

        #clear all old messages
        await text_input.channel.purge(limit=defaultval)
        #Change the current file to non active status
        file_name = "active_" + str(text_input.author.id) + ".txt"
        new_name = str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.rename(file_name, new_name)
            await text_input.channel.send("Campaign has been paused! Until next time!")

    elif text_input.content == "end mission":
        #end your campaign

        #clear all old messages
        await text_input.channel.purge(limit=defaultval)
        #Delete the file
        file_name = "active_" + str(text_input.author.id) + ".txt"
        if os.path.exists(file_name):
            os.remove(file_name)
            await text_input.channel.send("Campaign has ended! Safe travels")
    
    return

if __name__ == '__main__':
    engine()



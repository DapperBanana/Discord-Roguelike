import os
import os.path
import os
import glob
import time
import random
import numpy
from discord.ext import commands

#
#__________        _____                                         
#\______   \ _____/ ____\___________   ____   ____   ____  ____  
# |       _// __ \   __\/ __ \_  __ \_/ __ \ /    \_/ ___\/ __ \ 
# |    |   \  ___/|  | \  ___/|  | \/\  ___/|   |  \  \__\  ___/ 
# |____|_  /\___  >__|  \___  >__|    \___  >___|  /\___  >___  >
#        \/     \/          \/            \/     \/     \/    \/ 
#

enemy_list = {
    "m" : "12010",
    "b" : "22010",
    "s" : "32110",
    "p" : "22110",
    "w" : "45110",
    "S" : "99990", #I'm just working on the first level for now, I'll work on higher levels after the stats are fully fleshed out
    "I" : "99990",
    "W" : "99990",
    "!" : "99990",
    "?" : "00002", 
    "<" : "00003"
}

#Determines how to read the stats
stats_reader = {
    0 : "entity_val",
    1 : "char_sprite",
    2 : "strength",
    3 : "health",
    4 : "mana",
    5 : "level",
    6 : "item", #2 is random item, #3 is door, figured I could implement more item types as time goes on
    7 : "armor",
    8 : "weapon",
    9 : "entity_x",
    10 : "entity_y",
    11 : "next_direction",
    12 : "cycle_val",
    13 : "battle"
}

#How long the enemy path cycle is before deciding upon a new direction
enemy_path_list = {
    "m" : "4",
    "b" : "4",
    "s" : "4",
    "p" : "2",
    "w" : "9",
    "S" : "9",
    "I" : "9",
    "W" : "9",
    "!" : "9",
    "?" : "0",
    "<" : "0"
}

#
#  _________                      ________                          _________ __          __          
# /   _____/____ ___  __ ____    /  _____/_____    _____   ____    /   _____//  |______ _/  |_  ______
# \_____  \\__  \\  \/ // __ \  /   \  ___\__  \  /     \_/ __ \   \_____  \\   __\__  \\   __\/  ___/
# /        \/ __ \\   /\  ___/  \    \_\  \/ __ \|  Y Y  \  ___/   /        \|  |  / __ \|  |  \___ \ 
#/_______  (____  /\_/  \___  >  \______  (____  /__|_|  /\___  > /_______  /|__| (____  /__| /____  >
#        \/     \/          \/          \/     \/      \/     \/          \/           \/          \/ 
#

async def save_game_stats(raw_input, entity_list):
    author_name = raw_input.author.id
    numpy.savetxt("./player_files/info_" + str(author_name) + ".txt", entity_list, fmt='%s', delimiter=",")

#
#___________                           ____ ___            .___       __          
#\_   _____/__________   ____  ____   |    |   \______   __| _/____ _/  |_  ____  
# |    __)/  _ \_  __ \_/ ___\/ __ \  |    |   /\____ \ / __ |\__  \\   __\/ __ \ 
# |     \(  <_> )  | \/\  \__\  ___/  |    |  / |  |_> > /_/ | / __ \|  | \  ___/ 
# \___  / \____/|__|    \___  >___  > |______/  |   __/\____ |(____  /__|  \___  >
#     \/                    \/    \/            |__|        \/     \/          \/
#

async def force_update(raw_input, update_array):
    fname = "./player_files/info_" + str(raw_input.author.id) + ".txt"
    info_array = numpy.genfromtxt(fname, dtype=str, delimiter=",")
    entity_val = update_array[0]
    #load in old info
    for row in range(len(info_array)):
        if info_array[row][0] == entity_val:
            old_array = info_array[row]
    for element in range(len(update_array)):
        if update_array[element] == "NULL":
            update_array[element] = old_array[element]
    #next save it back to the info file
    for row in range(len(info_array)):
        if info_array[row][0] == entity_val:
            for val in range(len(info_array[row])):
                info_array[row][val] = update_array[val]
    await save_game_stats(raw_input, info_array)
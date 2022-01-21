import os
import os.path
import os
import glob
import time
import random
import numpy
from discord.ext import commands

#
# _______  _______  _______  _______  _______    _______  ______    _______  _______  _______  _______  ______   
#|       ||       ||   _   ||       ||       |  |       ||    _ |  |       ||   _   ||       ||       ||    _ |  
#|  _____||_     _||  |_|  ||_     _||  _____|  |       ||   | ||  |    ___||  |_|  ||_     _||   _   ||   | ||  
#| |_____   |   |  |       |  |   |  | |_____   |       ||   |_||_ |   |___ |       |  |   |  |  | |  ||   |_||_ 
#|_____  |  |   |  |       |  |   |  |_____  |  |      _||    __  ||    ___||       |  |   |  |  |_|  ||    __  |
# _____| |  |   |  |   _   |  |   |   _____| |  |     |_ |   |  | ||   |___ |   _   |  |   |  |       ||   |  | |
#|_______|  |___|  |__| |__|  |___|  |_______|  |_______||___|  |_||_______||__| |__|  |___|  |_______||___|  |_|
#

#First lets's make a list of what the entity stats are
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
    0 : "char_sprite",
    1 : "strength",
    2 : "health",
    3 : "mana",
    4 : "level",
    5 : "item", #2 is random item, #3 is door, figured I could implement more item types as time goes on
    6 : "entity_x",
    7 : "entity_y",
    8 : "next_direction",
    9 : "cycle_val",
    10 : "battle"
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

#Also have to check against 


async def save_game_stats(raw_input, entity_list):

    author_name = raw_input.author.id
    numpy.savetxt("info_" + str(author_name) + ".txt", entity_list, fmt='%s')


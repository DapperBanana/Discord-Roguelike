import discord
import level_generation
import numpy as np
from discord.ext import commands

client = commands.Bot(command_prefix = '.')

def blocks(infile, bufsize=1024):
    while True:
        try:
            data=infile.read(bufsize)
            if data:
                yield data
            else:
                break
        except:
            print("Error has occurred")

@client.event
async def on_message(input):
#
#    Just a basic test to see if the Bot is up and running
#
    if input.content == "test":
        await input.channel.send("The test is working.")
#
#    Creating the map and spitting it out on Discord
#
    if input.content == "create map":
        gen = level_generation.Generator()
        gen.gen_level()
        gen.gen_tiles_level()
        #with open('level.txt', 'r') as f:
        #    for c in blocks(f, 64):
        #        map_row = str(c)
        #        await input.channel.send("`{}`".format(map_row))
        await input.channel.send('Map Created!')
    await client.process_commands(input)
#
#    Test reading the txt file
#
    if input.content == "read text":
        f = open("Start_Screen.txt", "r")
        await input.channel.send("```" + f.read() + "```")

#
#    Test reading the map txt file
#
    if input.content == "read map":
        f = open("Screensize.txt", "r")
        await input.channel.send("```" + f.read() + "```")


@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

text_file = open("Info.txt", "r")
client_secret = text_file.read(59)
client.run(client_secret)

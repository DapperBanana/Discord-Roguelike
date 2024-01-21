import discord
import pickle
import os
import os.path
import time
import engine
from engine import check_user_id
from engine import engine
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer

intents = discord.Intents.default()
intents.messages = True  # Enable the on_message event

client = commands.Bot(command_prefix = '.', intents=intents)
defaultval = 100

@client.event
async def on_message(input):

#
#    Leave out messages from the Dungeon Bot
#
    if str(input.author.id) != "920859015146246184":
        if str(input.channel) == "the-catacombs":
            data_list = await check_user_id(input.author.id)
            await engine(input, data_list, client)

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def clear(ctx, amount=30):
    await ctx.channel.purge(limit=amount)

text_file = open("/home/pi/Info.txt", "r")
client_secret = text_file.read()
client.run(client_secret)

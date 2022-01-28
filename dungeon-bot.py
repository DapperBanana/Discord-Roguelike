import discord
import pickle
import os
import os.path
import time
import engine
from engine import check_user_id
from engine import engine
from discord.ext import commands

client = commands.Bot(command_prefix = '.')
defaultval = 100

@client.event
async def on_message(input):

#
#    Leave out messages from the Dungeon Bot
#
    if str(input.author.id) != "920859015146246184":
        if str(input.channel) == "bot-playground":
            data_list = await check_user_id(input.author.id)
            await engine(input, data_list)
    game_state = engine.music_state(input)
    if game_state == "active":
        voice_channel = discord.utils.get(input.guild.voice_channels, name="The Catacombs")
        await voice_channel.connect()
        voice = discord.utils.get(client.voice_clients, guild=input.guild)
        voice.play(discord.FFmpegPCMAudio("dungeon.mp3"))
    if game_state == "null":
        voice = discord.utils.get(client.voice_clients, guild=input.guild)
        if voice.is_connected():
            await voice.disconnect()

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def clear(ctx, amount=30):
    await ctx.channel.purge(limit=amount)

text_file = open("/home/pi/Info.txt", "r")
client_secret = text_file.read(59)
client.run(client_secret)

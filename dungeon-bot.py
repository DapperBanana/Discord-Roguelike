import discord
import pickle
import os
import os.path
import time
from engine import check_user_id
from engine import engine
from discord.ext import commands
from discord import FFmpegPCMAudio, PCMVolumeTransformer

intents = discord.Intents.all()
intents.messages = True  # Enable the on_message event

client = commands.Bot(command_prefix='.', intents=intents)
defaultval = 100

@client.event
async def on_message(message):

    if message.author == client.user:
        return
    
    if message.channel.name == "the-catacombs":
        if message.content.startswith('!play'):
            voice_channel = discord.utils.get(message.guild.voice_channels, name="the-catacombs-music")
    
            if voice_channel:
                voice = await voice_channel.connect()
                voice.play(discord.FFmpegPCMAudio('./music/dungeon_4.mp3'))
            else:
                await message.channel.send('I cannot find the voice channel named "the-catacombs-music".')
        data_list = await check_user_id(message.author.id)
        await engine(message, data_list, client)

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def clear(ctx, amount=30):
    await ctx.channel.purge(limit=amount)

@client.command()
async def hello(ctx):
    await ctx.channel.send(f'hello there {ctx.author.mention}')

text_file = open("/home/pi/Info.txt", "r")
bot_token = text_file.read()
client.run(bot_token)

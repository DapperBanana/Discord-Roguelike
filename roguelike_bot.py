import discord
from discord.ext import commands

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

text_file = open("Info.txt", "r")
client_secret = text_file.read(59)
client.run(client_secret)

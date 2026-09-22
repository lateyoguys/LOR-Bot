from pymongo import MongoClient
import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

cluster = MongoClient(MONGO_URI)
db = cluster["BotDatabase"]
collection = db["UserData"]

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="x!", intents=intents)



@bot.event
async def on_ready():
    print(f"{bot.user} online.")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    await bot.process_commands(message)

@bot.command()
async def start(ctx):
    query = {"user_id": ctx.author.id, "guild_id": ctx.guild.id}


    user_data = collection.find_one(query)

    if user_data:
        await ctx.reply(f"You already have a profile.")
        return

    new_user = {
        "user_id": ctx.author.id,
        "guild_id": ctx.guild.id,
        "balance": 100
    }

    collection.insert_one(new_user)


@bot.command()
async def reset(ctx):
    query = {"user_id": ctx.author.id, "guild_id": ctx.guild.id}

    user_data = collection.find_one(query)
    if not user_data:
        return await ctx.send("Use x!start to create a profile.")

    collection.delete_one(query)
    await ctx.send("Data wiped.")
    return None

@bot.command()
async def globalwipe(ctx):
    if ctx.author.id == 355010452796866560:
        collection.delete_many({})
        ctx.send("Data wiped.")
    else:
        await ctx.reply("Not authorized.")
    return None


@bot.command()
@commands.is_owner()  # Only you can run this
async def sync(ctx):
    await bot.tree.sync() # This syncs the commands globally
    await ctx.send("Slash commands synced successfully!")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
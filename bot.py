import discord
from discord.ext import commands

import json

import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("online")

@bot.command(brief="Sends the latency.") #honest steal, i cant bother to write a ping command https://stackoverflow.com/questions/46307035/latency-command-in-discord-py 
async def ping(ctx):
    await ctx.send('Pong! {0}'.format(round(bot.latency, 1)))

@bot.command(brief="Shows the current volume set on the VLC Player.", aliases=["gv"])
async def get_volume(ctx):
    # Shows the current volume
    with open("cfg.json", "r") as settings:
        cfg = json.load(settings)
        volume = cfg["volume"]
    await ctx.send(f"Current volume is {volume}. You can change it with >set_volume.")

@bot.command(brief="Sets the volume on the VLC Player.", aliases=["sv"])
async def set_volume(ctx, volume=None):
    if not volume:
        return await ctx.send("Must provide a value.")
    try:
        volume = int(volume)
    except:
        return await ctx.send("Value must be an integer.")

    if volume > 100 or volume < 0:
        return await ctx.send("Value cannot be more than 100 or less than 0.")
    
    with open("cfg.json", "r+") as settings:
        cfg = json.load(settings)
        settings.seek(0)

        cfg["volume"] = volume
        
        settings.truncate()
        json.dump(cfg, settings)
    await ctx.send(f"Volume set to {volume}.")

@bot.command(brief="Gets the currently playing vod.", aliases=["gcv"])
async def get_vod(ctx):
    with open("cfg.json", "r") as settings:
        cfg = json.load(settings)
        current_vod = cfg["current_vod"]
    
    await ctx.send(f"Currently playing: [{current_vod['title']}]({current_vod["url"]})")

@bot.command(brief="Removes a VOD from the list.", aliases=["rv"])
async def remove_vod(ctx, link=None):
    if not link:
        return await ctx.respond("Must provide a valid url.")
    with open("vods.json", "r+") as vj:
        vods = json.load(vj)
        vods = vods['vods'] # theres a way to simplify this yet i do not care.
        if link not in vods:
            return await ctx.send("URL not found in the VODs list.")

        vods.remove(link)
        vj.seek(0)
        vj.truncate()
        data = {"vods": vods}

        json.dump(data, vj)
    await ctx.send(f"Removed <{link}> from VODs list.")

@bot.command(brief="Adds a VOD to the list.", aliases=["av"])
async def add_vod(ctx, link=None):
    if not link:
        return await ctx.respond("Must provide a valid url.")
    with open("vods.json", "r+") as vj:
        vods = json.load(vj)
        vods = vods['vods'] # theres a way to simplify this yet i do not care.
        if link in vods:
            return await ctx.send("URL already in the VODs list.")

        vods.append(link)
        vj.seek(0)
        vj.truncate()
        data = {"vods": vods}

        json.dump(data, vj)
    await ctx.send(f"Added <{link}> to the VODs list.")

@bot.command(brief="Skips the current VOD.")
async def skip(ctx):
    with open("cfg.json", "r+") as settings:
        cfg = json.load(settings)
        cfg["skip"] = True

        settings.seek(0)
        settings.truncate()
        json.dump(cfg, settings)
    await ctx.send("Skipped the currently playing VOD.")

bot.run(token=token)
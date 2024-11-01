import os
import discord
from discord.ext import tasks, commands
from discord import default_permissions
import requests
import json
import cogs.sync as sync
import singelton.global_var as global_var

from services import log_service

intents = discord.Intents.all()
intents.members = True

bot = discord.Bot(intents=intents)

@bot.slash_command(description="Linke deinen GMod Account.")
async def link(ctx: discord.ApplicationContext, reg_key: str):

        try:
        
            response = requests.post("http://server:5000/link", json={"reg_key": reg_key, "discord_id": ctx.author.id})
            response.raise_for_status()

            data = response.json()
            
            await ctx.respond(data["message"],ephemeral=True)           
        
        except Exception as e:
            await ctx.respond(f"Error: {e}")

@bot.slash_command(description="Registriere deinen GMod Account.", default_permissions="administrator")
async def register(ctx: discord.ApplicationContext, steam_id: int):
        
        data = None

        try:
        
            response = requests.post(f"http://server:5000/register/{steam_id}")
            response.raise_for_status()

            data = response.json()
            
            await ctx.respond(data["message"])           
        
        except Exception as e:
            await ctx.respond(f"Error: {e}")

@bot.slash_command(description="Lade das Mapping der Ränge.", default_permissions="administrator")
async def map(ctx: discord.ApplicationContext, file: discord.Attachment):
        
        #check if file is a json file
        if file.filename[-5:] != ".json":
            await ctx.respond("Error: File is not a json file")
            return
        
        #check if file is build like {"data":[{"gmod_job": 123456789, "rank_id": 123456789}, ...]}
        data = None
        try:
            data = json.loads(await file.read())
        except Exception as e:
            await ctx.respond("Error: File is not build like {\"data\":[{\"gmod_job\": 123456789, \"rank_id\": 123456789}, ...]}")
            return

        try:
        
            response = requests.post("http://server:5000/map", json=data)
            response.raise_for_status()

            data = response.json()
            
            await ctx.respond(data["message"])           
        
        except Exception as e:
            await ctx.respond(f"Error: {e}")

@bot.slash_command(description="Get Stats", default_permissions="administrator")
async def stats(ctx: discord.ApplicationContext):
                
        message = global_var.get_stats()
        
        await ctx.respond(message)

@bot.event
async def on_ready():

    game = discord.Game("Rebellen-Zerstörungs Simulator")
    await bot.change_presence(activity=game)

    log_service.log(log_service.LogLevel.INFO, f"We have logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    log_service.log(log_service.LogLevel.INFO, f"Joined Guild {guild.name}")

    channel = guild.system_channel

    embed = discord.Embed(
        title="Hallo!",
        description="Ich bin zuständig um dich zu registrieren & deine Ränge zu updaten.",
        color=discord.Color.blue()
    )
    
    await channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    log_service.log(log_service.LogLevel.INFO, f"Left Guild {guild.name}")

@bot.event
async def on_slash_command_error(ctx, error):
    await ctx.respond(f"An error occured: {error}")

bot.add_cog(sync.Sync(bot))

bot.run(os.getenv("DISCORD_TOKEN"))

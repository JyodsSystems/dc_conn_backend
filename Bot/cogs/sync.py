import requests
import discord
import aiohttp
from discord.ext import tasks, commands
import services.log_service as log_service

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sync_loop_started = False


    def cog_unload(self):
        print("Unloading sync cog...")
        self.sync.cancel()


    async def fetch_user_ranks(self):
        try:
            url = "http://server:5000/dc/sync"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
            return {}

    async def fetch_watched_roles(self):
        try:
            url = "http://server:5000/dc/roles"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
            return []

    
    async def add_user_rank(self, discord_id, rank_id):
        try:
            guild = self.bot.get_guild(1281606978329645057) # Replace with your guild ID
            
            try:
                role = guild.get_role(rank_id)
            except Exception as e:
                print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                return False

            if role is None:
                return False
            
            try:
                guild_member = guild.get_member(discord_id)
            except Exception as e:
                print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                return False

            if guild_member is None:
                return False
            
            try:
                await guild_member.add_roles(role)
            except Exception as e:
                print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                return False
            
            return True
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
            return False
    
    async def remove_user_rank(self, discord_id, rank_id):
            try: 
            
                guild = self.bot.get_guild(1281606978329645057)

                try:
                    role = guild.get_role(rank_id)
                except Exception as e:
                    print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                    return

                if role is None:
                    return False
                
                try:
                    guild_member = guild.get_member(discord_id)
                except Exception as e:
                    print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                    return False

                if guild_member is None:
                    return False
                try:
                    await guild_member.remove_roles(role)
                except Exception as e:
                    print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}")) # Removed due to spam
                    return False
                return True
            except Exception as e:
                print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                return False
    
    async def sync_user_ranks(self, data):

        try:

            watched_roles = await self.fetch_watched_roles()

            watched_roles_array = []
            for role in watched_roles:
                watched_roles_array.append(role["dc_rank_id"])

            try:
                all_users = self.bot.get_guild(1281606978329645057).members
                all_roles = self.bot.get_guild(1281606978329645057).roles
            except Exception as e:
                print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
                return

            for user in all_users:
                if str(user.id) in data:
                    user_data = data[str(user.id)]
                    for role in all_roles:
                        if role.id in user_data:
                            if role.id in watched_roles_array:
                                await self.add_user_rank(user.id, role.id)
                        else:
                            if role.id in watched_roles_array:
                                await self.remove_user_rank(user.id, role.id)
                else:
                    for role in all_roles:
                        if role.id in watched_roles_array:
                            await self.remove_user_rank(user.id, role.id)
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.sync_loop_started:  # Verhindert, dass der Loop mehrmals gestartet wird
            print("Bot is ready, starting sync loop...")
            self.sync.start()
            self.sync_loop_started = True

    @tasks.loop(seconds=15)
    async def sync(self):
        print("Sync loop is running...")
        print(log_service.log(log_service.LogLevel.INFO, "Syncing data..."))
        try:
            data = await self.fetch_user_ranks()
            await self.sync_user_ranks(data)
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error in sync loop: {e}"))
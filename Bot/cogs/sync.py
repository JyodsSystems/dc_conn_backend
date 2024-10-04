import requests
import discord
import aiohttp
import time
import asyncio
import singelton.global_var as global_var
from discord.ext import tasks, commands
import services.log_service as log_service

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sync_loop_started = False
        self.timeout = aiohttp.ClientTimeout(total=10)


    def cog_unload(self):
        print("Unloading sync cog...")
        self.sync.cancel()


    async def fetch_user_ranks(self):
        try:

            curr_time = time.time()

            url = "http://server:5000/dc/sync"
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    response.raise_for_status()

                    log_service.log(log_service.LogLevel.INFO, f"Fetched user ranks in {time.time() - curr_time} seconds.")

                    return await response.json()
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
            return {}

    async def fetch_watched_roles(self):
        try:

            curr_time = time.time()

            url = "http://server:5000/dc/roles"
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    response.raise_for_status()

                    log_service.log(log_service.LogLevel.INFO, f"Fetched watched roles in {time.time() - curr_time} seconds.")

                    return await response.json()
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))
            return []

    
    async def add_user_rank(self, discord_id, rank_id):
        try:

            await asyncio.sleep(0.1)

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

                await asyncio.sleep(0.1)
            
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

                member_roles = user.roles

                curr_time = time.time()

                log_service.log(log_service.LogLevel.INFO, f"Syncing user {user.id}... with roles {member_roles}")

                if str(user.id) in data:
                    user_data = data[str(user.id)]

                    log_service.log(log_service.LogLevel.INFO, f"UserData: {user_data} for user {user.id}")

                    for role in all_roles:
                        if role.id in user_data:
                            if role.id in watched_roles_array and role not in member_roles:
                                log_service.log(log_service.LogLevel.INFO, f"Wanted to add role {role.id} to user {user.id}")
                                await self.add_user_rank(user.id, role.id)
                        else:
                            if role.id in watched_roles_array and role in member_roles:
                                log_service.log(log_service.LogLevel.INFO, f"Wanted to remove role {role.id} from user {user.id}")
                                await self.remove_user_rank(user.id, role.id)
                else:
                    for role in all_roles:
                        if role.id in watched_roles_array and role in member_roles:
                            log_service.log(log_service.LogLevel.INFO, f"Wanted to remove role {role.id} from user {user.id}")
                            await self.remove_user_rank(user.id, role.id)

                print(log_service.log(log_service.LogLevel.INFO, f"Syncing user {user.id} took {time.time() - curr_time} seconds."))

                now = time.time()

                formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))

                global_var.set_stats("synced_users", len(all_users))
                global_var.set_stats("synced_roles", len(all_roles))

            
            log_service.log(log_service.LogLevel.INFO, "Synced user ranks.")

        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error: {e}"))

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.sync_loop_started:  # Verhindert, dass der Loop mehrmals gestartet wird
            print("Bot is ready, starting sync loop...")
            self.sync.start()
            self.sync_loop_started = True

    @tasks.loop(minutes=1)
    async def sync(self):

        curr_sys_time = time.time()

        print("Sync loop is running...")
        print(log_service.log(log_service.LogLevel.INFO, "Syncing data..."))
        try:
            data = await self.fetch_user_ranks()
            await self.sync_user_ranks(data)
        except Exception as e:
            print(log_service.log(log_service.LogLevel.ERROR, f"Error in sync loop: {e}"))

        print(log_service.log(log_service.LogLevel.INFO, f"Syncing took {time.time() - curr_sys_time} seconds."))

        now = time.time()

        # Format current time for last_sync and last_duration
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
        last_duration_formatted = time.strftime('%H:%M:%S:%f', time.gmtime(time.time() - curr_sys_time))

        # Set global statistics
        global_var.set_stats("last_sync", formatted_time) 
        global_var.set_stats("last_duration", last_duration_formatted) 
        global_var.set_stats(f"duration_{str(now)}", time.time() - now)
        global_var.set_median()
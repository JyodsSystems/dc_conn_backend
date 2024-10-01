import requests
import discord
from discord.ext import tasks, commands
import services.log_service as log_service

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sync.start()

    def cog_unload(self):
        print("Unloading sync cog...")
        self.sync.cancel()

    def fetch_user_ranks(self):
        url = "http://server:5000/dc/sync"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    async def add_user_rank(self, discord_id, rank_id):
        
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
    
    async def remove_user_rank(self, discord_id, rank_id):
            
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
    
    async def sync_user_ranks(self, data):
        
        print(log_service.log(log_service.LogLevel.INFO, "Syncing data2..."))
        
        ignore_roles = [1281607139869327462, 1281765283781935114, 1281765572408774696] # Replace with your role IDs

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
                        if role.id not in ignore_roles:
                            await self.add_user_rank(user.id, role.id)
                    else:
                        if role.id not in ignore_roles:
                            await self.remove_user_rank(user.id, role.id)
            else:
                for role in all_roles:
                    if role.id not in ignore_roles:
                        await self.remove_user_rank(user.id, role.id)


    @tasks.loop(seconds=30)
    async def sync(self):
        print(log_service.log(log_service.LogLevel.INFO, "Syncing data..."))
        data = self.fetch_user_ranks()
        await self.sync_user_ranks(data)
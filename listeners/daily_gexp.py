import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
import json
import pytz
import discord
import requests
import discord.ui
import os
from dotenv import load_dotenv

# Open the JSON file and read in the data
with open('config.json') as json_file:
    data = json.load(json_file)


enable_feature = bool(data["features"]["auto_daily_gexp"])

embed_color = int(data["general"]["embed_color"].strip("#"), 16) #convert hex color to hexadecimal format
hypixel_guild_id = data["hypixel_ids"]["guild_id"]
daily_points_channel_id = int(data["text_channel_ids"]["daily_guild_points"])
guild_id = int(data["general"]["discord_server_guild_id"])
command_prefix = data["general"]["bot_prefix"]

already_sent = False

class dailygpoints(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.guild_id = guild_id
        self.dailygpoints.start()
        self.total_points = 0  # Initialize the total points variable

    @tasks.loop(seconds=20)  # Run every 20 seconds
    async def dailygpoints(self):
        global already_sent
        if enable_feature:
            channel = self.client.get_channel(daily_points_channel_id)
            est = pytz.timezone('US/Eastern')
            current_time = datetime.now(est)
            
            if current_time.hour == 00 and current_time.minute == 00: # mid night EST
                if not already_sent:
                    
                    # Load the "verified_accounts.json" file as a dictionary
                    with open('verified_accounts.json', 'r') as verified_file:
                        verified_accounts = json.load(verified_file)
                        
                    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                    hypixel_api_key = os.getenv("HYPIXEL_API_KEY")
                    api_link = f'https://api.hypixel.net/guild?key={hypixel_api_key}&id={hypixel_guild_id}'
                    response = requests.get(api_link)

                    if response.status_code == 200:
                        data = response.json()
                        member_data = data['guild']['members']
                        guild_name = data['guild']['name']
                        try:
                            guild_tag = f" [{data['guild']['tag']}]"
                        except KeyError:
                            guild_tag = ""
                        formatted_member_info = []
                        

                        # Initialize the total points variable for each iteration
                        self.total_points = 0
                        
                        max_contributors = 25

                        for i, member in enumerate(member_data[:max_contributors], start=1):
                            user_uuid = member['uuid']
                            experience = member['expHistory'].get(yesterday_date, 0)
                            self.total_points += experience  # Update the total points
                            
                            # Check if the UUID matches a verified account and format the user string
                            discord_id = None
                            for discord_user_id, account_data in verified_accounts.items():
                                if account_data.get('uuid') == user_uuid:
                                    discord_id = discord_user_id
                                    break

                            if discord_id:
                                user_string = f"<@{discord_id}>"
                            else:
                                playerdb_url = f'https://playerdb.co/api/player/minecraft/{user_uuid}'
                                username_requests = requests.get(playerdb_url)
                                user_data = username_requests.json()
                                username = user_data["data"]["player"]["username"]
                                user_string = username
                            
                            formatted_info = f"**{i}.** {user_string} - **{experience}** GEXP"
                            formatted_member_info.append(formatted_info)

                        while len(formatted_member_info) < max_contributors:
                            i = len(formatted_member_info) + 1
                            formatted_info = f"**{i}.** Empty Member Slot - **0** GEXP"
                            formatted_member_info.append(formatted_info)

                        formatted_member_string = '\n'.join(formatted_member_info)
                        
                        guild = self.client.get_guild(self.guild_id)
                        guild_icon_url = guild.icon.url
                        
                        embed = discord.Embed(
                            title = f"**🏆 | {guild_name}{guild_tag} Daily GEXP Report**", 
                            description=f"""
                            **{format(self.total_points, ",")}** Total GEXP was earned on `{yesterday_date}`.
                            
                            **Top {max_contributors} GEXP Contributors:**
                            {formatted_member_string}
                            
                            Hypixel GEXP resets every 24 hours at 12AM EST.
                            """,
                            colour = embed_color
                            )
                        embed.set_thumbnail(url = guild_icon_url)
                        embed.timestamp = datetime.now()
                        embed.set_footer(text=f"©️ {guild.name}", icon_url = guild_icon_url)
                        await channel.send(embed=embed)
                    
                    already_sent = True
                else:
                    pass
            else:
                already_sent = False
        else:
            pass
        
        
async def setup(client):
    await client.add_cog(dailygpoints(client))
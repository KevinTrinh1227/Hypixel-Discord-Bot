import discord
from discord.ext import tasks, commands
import datetime
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

enable_feature = bool(data["features"]["server_stats"])


#json data to get channel IDs
command_prefix = data["general"]["bot_prefix"]
member_role_id = int(data["role_ids"]["unverified_member"])
member_count_chanel_id = int(data["voice_channel_ids"]["member_count"])
members_online_channel_id = int(data["voice_channel_ids"]["members_online"])
guild_member_online_channel_id = int(data["voice_channel_ids"]["guild_member_online"])
guild_member_role_id = int(data["role_ids"]["guild_member"])


#global variables for channel name usage
global_member_count = 0
global_online_members = 0
global_online_and_guild_membery = 0


class serverstats(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.serverstats.start()
    
    
    @tasks.loop(seconds=301.0)
    async def serverstats(self):

        """
        print(enable_feature)
        print(type(enable_feature))
        """

        # Open the JSON file and read in the data
        with open('config.json') as json_file:
            data = json.load(json_file)

        enable_feature = bool(data["features"]["server_stats"])


        #json data to get channel IDs
        member_count_chanel_id = int(data["voice_channel_ids"]["member_count"])
        members_online_channel_id = int(data["voice_channel_ids"]["members_online"])
        guild_member_online_channel_id = int(data["voice_channel_ids"]["guild_member_online"])
        guild_member_role_id = int(data["role_ids"]["guild_member"])

        #if the feature is enabled then it will run
        if enable_feature:
            
            member_count_channel = self.client.get_channel(member_count_chanel_id) #ID of voice channel that changes
            members_online_channel = self.client.get_channel(members_online_channel_id) #ID of voice channel online members
            guild_member_online_channel = self.client.get_channel(guild_member_online_channel_id) #guild_member online voice channel
            guild_membery_role = discord.utils.get(self.client.guilds[0].roles, id=guild_member_role_id)
        
        
            #if a change has been detected.
            #this helps with being rate limited by discord
            
            member_count = len(self.client.guilds[0].members)
            global global_member_count
            if (global_member_count != member_count):
                global_member_count = member_count
                await member_count_channel.edit(name=f"Member Count: {member_count}")
            else:
                pass
            
            online_members = [member for member in self.client.guilds[0].members if member.status != discord.Status.offline]
            global global_online_members
            if (global_online_members != online_members):
                global_online_members = online_members
                await members_online_channel.edit(name=f"Online Members: {len(online_members)}")
            else:
                pass
            
            online_and_guild_membery_members = [member for member in self.client.guilds[0].members if guild_membery_role in member.roles and member.status != discord.Status.offline]
            global global_online_and_guild_membery
            if (global_online_and_guild_membery != online_and_guild_membery_members):
                global_online_and_guild_membery = online_and_guild_membery_members
                await guild_member_online_channel.edit(name=f"Guild Online: {len(online_and_guild_membery_members)}/125")
            else:
                pass

        else:
            pass
        
        
async def setup(client):
    await client.add_cog(serverstats(client))
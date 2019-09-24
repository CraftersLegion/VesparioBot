"""

Program Name: cBot
Version: 1.0
Description: A Discord Bot & Announcement Manager

Date Created: 13/01/2019

Author: Randamonium NZ Ltd.
Website: http://www.randamonium.co.nz

"""

# Import Modules
import os
import configparser
import discord
import emoji
import urllib.request
from mcstatus import MinecraftServer
import time

# Bot Setup
client = discord.Client()
applications = configparser.ConfigParser()
applications.read("config.rcf")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    channel = client.get_channel(557700585856434186)
    await channel.send("Haven Realms Bot Now Online\n----------------------------\n")
    try:
        website = urllib.request.Request("https://www.havenrealms.net/", headers={'User-Agent' : "HavenRealms Bot"})
        status = urllib.request.urlopen(website).getcode()
        await channel.send("**Website Satus:** Online")
    except urllib.error.HTTPError:
        await channel.send("**Website Status:** Offline")
    
@client.event
async def on_member_join(member):

    # Announce New Member to Community
    channel = client.get_channel(557701504283181072)
    await channel.send("Hey everyone, please welcome <@" + str(member.id) + "> to Haven Realms!")

    # Add Member Role
    role = member.guild.get_role(536507066978926613)
    await member.add_roles(role)

@client.event
async def on_reaction_add(reaction, author):
    if str(author.id) in applications:
        if applications.get(str(author.id), "channel") == str(reaction.message.channel.id):
            if reaction.emoji == "\U0000274e":
                await reaction.message.channel.delete()

@client.event
async def on_message(message):

    # Check if Applying
    if message.channel.id == 625123233586348053:
        if message.content == "!apply":

            # Delete Message
            await message.channel.delete_messages([message])

            # Check if Already Applied
            if not applications.has_section(str(message.author.id)):
                
                # Define Variables
                applicationsCategory = client.get_channel(625122093423525899)
                overwrites = {
                    message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    message.author: discord.PermissionOverwrite(read_messages=True)
                }

                # Create New Channel
                newApplication = await message.guild.create_text_channel(str("application-" + message.author.name), category=applicationsCategory, overwrites=overwrites)

                # Notify Applicant
                embed = discord.Embed( title=str(message.author.name + " Application"), description=("Your application has now be successfully started " + message.author.mention + ", you can start your application here: " + newApplication.mention), colour=48383)
                embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                notify = await message.channel.send(embed=embed)

                # Add Information to Config
                applications.add_section(str(message.author.id))
                applications.set(str(message.author.id), "channel", str(newApplication.id))
                applications.set(str(message.author.id), "status", "open")

                # Application Init Message
                tickEmoji = "\U00002705"
                crossEmoji = "\U0000274e"
                embed = discord.Embed(title="**Start Your Application**", description="**Welcome to Haven Realms **\nThank you for showing your interest in the show and we hope to see you join as a member of our team. To start your application please react with a :white_check_mark: or alternatively if you wish to cancel your application you can react with a :negative_squared_cross_mark:.\n\n**React Below to Start Your Application:**", colour=48383)
                embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                newMessage = await newApplication.send(embed=embed)

                # Add Reactions
                await newMessage.add_reaction(tickEmoji)
                await newMessage.add_reaction(crossEmoji)

                time.sleep(5)
                await message.channel.delete_messages([notify])
            

    elif message.author != client.user:
        # Define Variables
        if message.content.startswith("!"):
            command = message.content.replace("!", "", 1)
            commandList = command.split(" ")
            if commandList[0] == "wiki":
                if commandList[1] == "servers" or commandList[1] == "server":
                    if commandList[2] == "farmtycoon":
                        embed = discord.Embed( title="Official FarmTycoon Wiki", description="You can find the official FarmTycoon Wiki (here)[https://www.havenrealms.net/wiki/servers/farmtycoon/]", colour=48383)
                        embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                        await message.channel.send(embed=embed)
                    else:
                        await message.channel.send("What are you trying to do? I'm not made of magic.")
                else:
                    await message.channel.send("What are you trying to do? I'm not made of magic.")
            if command == "invite":
                embed = discord.Embed( title="Official Discord Invite Link", description="For inviting friends or more people to our community please send them the official Discord invite link: [https://discord.gg/UuCgJbZ](https://discord.gg/UuCgJbZ)", colour=48383)
                embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                await message.channel.send(embed=embed)
            elif command.startswith("ip"):
                if command == "ip all":
                    embed = discord.Embed( title="Official Server Addresses", description=":crystal_ball: **Hub:** play.havenrealms.net**/**hub.havenrealms.net\n:corn: **FarmTycoon:** farmtycoon.havenrealms.net\n:dragon_face: **Palegio:** palegio.havenrealms.net\n\nor alternatively you can go to all through the Hub.", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
                elif command == "ip hub":
                    embed = discord.Embed( title="Official Hub Address", description=":crystal_ball: **Hub:** play.havenrealms.net**/**hub.havenrealms.net", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
                elif command == "ip farmtycoon":
                    embed = discord.Embed( title="Official FarmTycoon Address", description=":corn: **FarmTycoon:** farmtycoon.havenrealms.net", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
                elif command == "ip palegio":
                    embed = discord.Embed( title="Official Palegio Address", description=":dragon_face: **Palegio:** palegio.havenrealms.net", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed( title="Official Server Addresses", description="For a full list of our servers, please use \"!ip all\" otherwise use \"!ip <server>\"", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
            elif command.startswith("status"):
                if command == "status":
                    embed = discord.Embed( title="Official Server Addresses", description=":crystal_ball: **Hub:** Online\n:corn: **FarmTycoon:** Online\n:dragon_face: **Palegio:** Offline", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
                elif command == "status website":
                    try:
                        website = urllib.request.Request("https://www.havenrealms.net/", headers={'User-Agent' : "HavenRealms Bot"})
                        status = urllib.request.urlopen(website).getcode()
                        if str(status) == "200":
                            embed = discord.Embed( title="Website Status", description="**ONLINE**", colour=48383)
                            await message.channel.send(embed=embed)
                        else:
                            embed = discord.Embed( title="Website Status", description="**OFFLINE**", colour=48383)
                            await message.channel.send(embed=embed)
                    except urllib.error.HTTPError:
                        embed = discord.Embed( title="Website Status", description="**OFFLINE**", colour=48383)
                        await message.channel.send(embed=embed)
                elif command == "status debug":
                    server = MinecraftServer.lookup("play.havenrealms.net:25565")
                    status = server.status()
                    print(status)
                else:
                    embed = discord.Embed( title="Network Status Checker", description="Coming Soon", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)
            elif command.startswith("pack"):
                    embed = discord.Embed( title="Haven Realms Resource Pack", description="Download master pack from [here](https://github.com/HavenRealms/HavenPack/archive/master.zip).", colour=48383)
                    embed.set_thumbnail(url="https://www.havenrealms.net/wp-content/uploads/2018/08/cropped-Logo-Icon-1.png")
                    await message.channel.send(embed=embed)

        # Jokes
        if "yay" in message.content.lower().split(" "):
            await message.channel.send("YAY!!!")
        if "cool" in message.content.lower().split(" "):
            await message.channel.send("Cool Cool Cool")
        if "pol" in message.content.lower().split(" "):
            await message.channel.send("POL! That's so funny!")
        if "elx" in message.content.lower().split(" ") or "dan" in message.content.lower().split(" "):
            await message.channel.send("<@278039451022917633> they're doing it again!")
        if "prasun" in message.content.lower().split(" "):
            await message.channel.send("Prasun is a Raisin")
        if "blue" in message.content.lower().split(" "):
            await message.channel.send("Blue is a bald dentist.")
        if "that" in message.content.lower().split(" "):
            await message.channel.send("Thatty that that!")
        if "will" in message.content.lower().split(" "):
            await message.channel.send("Oh no! The \"umu\" has awoken!")
        if "nw" in message.content.lower().split(" "):
            await message.channel.send("It means no worries! For the rest of your days!")
            
async def yt(author, url):
    voice_channel = author.voice
    vc = await client.join_voice_channel(voice_channel)

    player = await vc.create_ytdl_player(url)
    player.start()

client.run("token")


import discord
from discord.ext import commands

class Admin:
    def __init__(self, bot):
        
        # Define Variables
        self.bot = bot
    
    admins = [
        536507052558909461, # Network Owner
        607066198315892797, # Server Owner
        536507057550131221, # Manager
        536507054064402437, # Head Admin
        536507055402516510  # Admin
    ]

    @commands.command(hidden = True)
    @commands.has_any_role(admins)
    async def announce(self, ctx, *, message):
        await ctx.message.delete()
        channel = self.bot.get_channel(554496970266378240)
        await channel.send(embed=discord.Embed(title = 'Announcement!', description = message, colour = discord.Colour.blurple()))

def setup(bot): bot.add_cog(Admin(bot))

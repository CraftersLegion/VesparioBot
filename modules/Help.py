import discord
from discord.ext import commands
from modules.Paginator import HelpPaginator

class Help(commands.Cog):
    def __init__(self,bot):

        # Define Variables
        self.bot = bot

        bot.remove_command('help')

    @commands.command()
    async def help(self, ctx, *, command = None):
        '''Get help with using Vespario.'''
        if not command: page = await HelpPaginator.from_bot(ctx)
        else:
            entry = self.bot.get_cog(command) or self.bot.get_command(command)

            if not entry:
                command = command.replace('@', '@\u200b')
                return await ctx.send(embed = discord.Embed(title = f'I couldn\'t find **{command}**.', description = 'This command either doesn\'t exist or is spelled incorrectly. Please try again.', colour = discord.Colour.red()))
            
            elif isinstance(entry, commands.Command): page = await HelpPaginator.from_command(ctx, entry)
            
            else: page = await HelpPaginator.from_cog(ctx, entry)
        
        await p.paginate()

def setup(bot): bot.add_cog(Help(bot))
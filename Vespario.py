import discord
from discord.ext import commands

modules = [
    'modules.Miscellaneous',
    'modules.Help',
    'modules.Admin',
    'modules.Levels' # TODO: Add level system later on
    ]

class Vespario(commands.Bot):
    def __init__(self):
        self.prefix = '!'
        super().__init__(command_prefix = commands.when_mentioned_or(self.prefix), case_insensitive = True)

    def run(self):
        for module in modules:
            try:
                self.load_extension(module)
                print(f'[{module}] Loaded')

            except Exception as e: print(f'[{type(e).__name__}] {e}')

        super().run('BOT_TOKEN')

    async def on_ready(self):
        await self.change_presence(activity = discord.Activity(name = f'{self.prefix}help',type = 2))
        print('Vespario is ready to go!')

    async def on_member_join(self, member):
        channel = self.get_channel(557701504283181072)
        await channel.send(f'Welcome to Haven Realms, {member.mention}!')

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown): return await ctx.send(embed = discord.Embed(title = 'Slow down!', description = f'Try `{self.prefix}{ctx.command}` again in **{round(error.retry_after)}** seconds.', colour = discord.Colour.red()))
        elif isinstance(error, commands.MissingRequiredArgument): return await ctx.send(embed = discord.Embed(title = 'You forgot some arguments.', description = f'Need help with command arguments? Use **{self.prefix}help**.', colour = discord.Colour.red()))
        elif isinstance(error, commands.BadArgument): return await ctx.send(embed = discord.Embed(title = 'The arguments given are invalid.', description = f'Need help with command arguments? Use **{self.prefix}help**.', colour = discord.Colour.red()))
        elif isinstance(error, commands.NotOwner): return await ctx.send(embed = discord.Embed(title = 'You aren\'t allowed to do that.', colour = discord.Colour.red())) 
        elif isinstance(error, commands.CommandNotFound): pass
        else:print(e)

    async def on_message(self, message):
        if message.author.bot: return
        await self.process_commands(message)

if __name__ == '__main__': Vespario().run()
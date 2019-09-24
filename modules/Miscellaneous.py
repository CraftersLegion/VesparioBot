import discord
from discord.ext import commands
import datetime

class Miscellaneous(commands.Cog):
	def __init__(self, bot):
		
		# Define Variables
		self.bot = bot

	async def on_ready(self): self.uptime = datetime.datetime.utcnow()

	def get_uptime(self):
		delta = datetime.datetime.utcnow() - self.uptime
		hours, remainder = divmod(int(delta.total_seconds()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		d = '' if days == 1 else 's'
		h = '' if hours == 1 else 's'
		m = '' if minutes == 1 else 's'
		s = '' if seconds == 1 else 's'

		if days: format = f'**{days}** day{d}, **{hours}** hour{h}, **{minutes}** minute{m} and **{seconds}** second{s}'
		else: format = f'**{hours}** hour{h}, **{minutes}** minute{m} and **{seconds}** second{s}'
		return format

	@commands.command(aliases = ['suggestion', 'feedback'])
	async def suggest(self, ctx, *, suggestion):
		'''Leave a suggestion!'''
		
		channel = self.bot.get_channel(536507128320491530)

		await channel.send(embed=discord.Embed(title = 'New Suggestion!', description = f'{ctx.author} suggests **{suggestion}**.', colour = discord.Colour.blurple()))
		await ctx.send(embed=discord.Embed(title='Your suggestion was noted! **Thank you!**', description = 'Abuse of this system will result in a punishment to be decided by the staff team.', colour = discord.Colour.green()))

	@commands.command()
	async def apply(self, ctx):
		await ctx.send('This feature is coming soon. You\'ll have to wait until then!')
	
def setup(bot): bot.add_cog(Miscellaneous(bot))
import asyncio
import discord
class Pages:
    def __init__(self, ctx, *, entries, per_page = 12, show_entry_count = True):
        self.bot      = ctx.bot
        self.entries  = entries
        self.message  = ctx.message
        self.channel  = ctx.channel
        self.author   = ctx.author
        self.per_page = per_page

        pages, left_over = divmod(len(self.entries), self.per_page)
        if left_over: pages += 1

        self.maximum_pages    = pages
        self.embed            = discord.Embed(colour = discord.Colour.blurple())
        self.paginating       = len(entries) > per_page
        self.show_entry_count = show_entry_count
        self.reaction_emojis  = [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.first_page),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK SQUARE FOR STOP}', self.stop_pages),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.last_page)
            ]

        if ctx.guild is not None: self.permissions = self.channel.permissions_for(ctx.guild.me)
        else: self.permissions = self.channel.permissions_for(ctx.bot.user)

    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base : base + self.per_page]

    async def show_page(self, page, *, first = False):
        self.current_page = page
        entries           = self.get_page(page)
        p                 = []

        for index, entry in enumerate(entries, 1 + ((page - 1) * self.per_page)): p.append(f'{index}) {entry}')

        if self.maximum_pages > 1:
            if self.show_entry_count: text = f'Page {page}/{self.maximum_pages} ({len(self.entries)} entries)'
            else: text = f'Page {page} of {self.maximum_pages}'
            self.embed.set_footer(text = text)

        if not self.paginating:
            self.embed.description = '\n'.join(p)
            return await self.channel.send(embed = self.embed)

        if not first:
            self.embed.description = '\n'.join(p)
            return await self.message.edit(embed = self.embed)

        p.append('')
        p.append('Confused? Click on \N{INFORMATION SOURCE} for more info.')

        self.embed.description = '\n'.join(p)
        self.message           = await self.channel.send(embed=self.embed)

        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'): continue
            await self.message.add_reaction(reaction)

    async def checked_show_page(self,page):
        if page != 0 and page <= self.maximum_pages: await self.show_page(page)

    async def first_page(self): await self.show_page(1)

    async def last_page(self): await self.show_page(self.maximum_pages)

    async def next_page(self): await self.checked_show_page(self.current_page + 1)

    async def previous_page(self): await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating: await self.show_page(self.current_page)

    async def stop_pages(self):
        await self.message.delete()
        self.paginating = False

    def react_check(self,reaction,user):
        if user is None or user.id != self.author.id: return False
        if reaction.message.id != self.message.id: return False
        for (emoji, function) in self.reaction_emojis:
            if reaction.emoji == emoji:
                self.match = function
                return True
        return False

    async def paginate(self):
        first_page = self.show_page(1, first = True)

        if not self.paginating: await first_page
        else: self.bot.loop.create_task(first_page)
        while self.paginating:
            try: reaction, user = await self.bot.wait_for('reaction_add', check = self.react_check, timeout = 30)
            except asyncio.TimeoutError:
                self.paginating = False
            
                try: await self.message.clear_reactions()
                except: pass
                finally: break

            try: await self.message.remove_reaction(reaction, user)
            except: pass

            await self.match()

class FieldPages(Pages):
    async def show_page(self, page, *, first = False):
        self.current_page = page
        entries           = self.get_page(page)

        self.embed.clear_fields()

        self.embed.description = discord.Embed.Empty

        for key, value in entries: self.embed.add_field(name = key, value = value, inline = False)

        if self.maximum_pages > 1:
            if self.show_entry_count: text = f'Page {page}/{self.maximum_pages} ({len(self.entries)} entries)'
            else: text = f'Page {page}/{self.maximum_pages}'
            self.embed.set_footer(text = text)

        if not self.paginating: return await self.channel.send(embed = self.embed)
        if not first: return await self.message.edit(embed = self.embed)

        self.message = await self.channel.send(embed = self.embed)
        
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'): continue
            await self.message.add_reaction(reaction)

import itertools
import inspect
import re

_mention = re.compile(r'<@\!?([0-9]{1,19})>')

def cleanup_prefix(bot, prefix):
    mention = _mention.match(prefix)

    if mention:
        user = bot.get_user(int(m.group(1)))
        if user: return f'@{user.name} '
    return prefix

async def _can_run(cmd, ctx):
    try: return await cmd.can_run(ctx)
    except: return False

def _command_signature(cmd):
    result = [cmd.qualified_name]

    if cmd.usage:
        result.append(cmd.usage)
        return' '.join(result)

    params = cmd.clean_params

    if not params: return' '.join(result)

    for name, param in params.items():
        if param.default is not param.empty:
            should_print = param.default if isinstance(param.default, str) else param.default is not None
            if should_print: result.append(f'[{name} = {param.default!r}]')
            else:result.append(f'[{name}]')

        elif param.kind == param.VAR_POSITIONAL:result.append(f'[{name}...]')
        else: result.append(f'({name})')

    return' '.join(result)

class HelpPaginator(Pages):
    def __init__(self, ctx, entries, *, per_page = 4):
        super().__init__(ctx, entries = entries, per_page = per_page)
        self.reaction_emojis.append(('\N{WHITE QUESTION MARK ORNAMENT}', self.show_bot_help))
        self.total = len(entries)

    @classmethod
    async def from_cog(cls, ctx, cog):
        cog_name         = cog.__class__.__name__
        entries          = sorted(ctx.bot.get_cog_commands(cog_name), key = lambda c:c.name)
        entries          = [cmd for cmd in entries if (await _can_run(cmd, ctx)) and not cmd.hidden]
        self             = cls(ctx,entries)
        self.title       = f'**{cog_name}** Commands'
        self.description = inspect.getdoc(cog)
        self.prefix      = cleanup_prefix(ctx.bot, ctx.prefix)

        return self

    @classmethod
    async def from_command(cls, ctx, command):
        try: entries = sorted(command.commands, key = lambda c:c.name)
        except AttributeError: entries = []
        else: entries = [cmd for cmd in entries if (await _can_run(cmd, ctx)) and not cmd.hidden]

        self = cls(ctx, entries)
        self.title = command.signature

        if command.description: self.description = f'{command.description}\n\n{command.help}'
        else: self.description = command.help or 'No description'

        self.prefix = cleanup_prefix(ctx.bot, ctx.prefix)

        return self

    @classmethod
    async def from_bot(cls, ctx):
        def key(c): return c.cog_name or ''
        entries      = sorted(ctx.bot.commands, key = key)
        nested_pages = []
        per_page     = 10

        for cog, commands in itertools.groupby(entries, key = key):
            plausible = [cmd for cmd in commands if (await _can_run(cmd, ctx)) and not cmd.hidden]
            
            if len(plausible) == 0: continue

            description = ctx.bot.get_cog(cog)

            if description is None: description = discord.Embed.Empty
            else: description = inspect.getdoc(description) or discord.Embed.Empty
            nested_pages.extend((cog, description, plausible[i : i + per_page]) for i in range(0, len(plausible), per_page))
        
        self = cls(ctx, nested_pages, per_page = 1)
        self.prefix   = cleanup_prefix(ctx.bot, ctx.prefix)
        self.get_page = self.get_bot_page
        self._is_bot  = True
        self.total    = sum(len(o) for _, _, o in nested_pages)
        
        return self
    
    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        self.title                 = f'**{cog}** Commands'
        self.description           = description
        
        return commands
    
    async def show_page(self, page, *, first = False):
        self.current_page = page
        entries           = self.get_page(page)

        self.embed.clear_fields()
        self.embed.description = self.description
        self.embed.title       = self.title

        if hasattr(self, '_is_bot'): self.embed.add_field(name = 'Links', value='\u2022 [Support](<#554773144338956308>) \u2022 [Donate](https://donatebot.io/checkout/536506218945052692?buyer=257575046288113665) \u2022 [Website](https://havenrealms.net)')
        self.embed.set_footer(text = f'Use "{self.prefix}help (command/module)" for more info.')

        signature = _command_signature

        for entry in entries: self.embed.add_field(name = signature(entry), value = entry.short_doc or "No description", inline = False)
        
        if self.maximum_pages: self.embed.set_author(name = f'Page {page}/{self.maximum_pages} ({self.total} commands)')
        if not self.paginating: return await self.channel.send(embed = self.embed)
        if not first: return await self.message.edit(embed = self.embed)
        
        self.message = await self.channel.send(embed = self.embed)
        
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'): continue
            await self.message.add_reaction(reaction)

    async def show_bot_help(self):
        self.embed.title = f'Using **Vespario**'
        
        self.embed.clear_fields()
        
        entries = (
            ('**(**argument**)**', 'This means the argument is **required**.'),
            ('**[**argument**]**', 'This means the argument is **optional**.'),
            ('[A | B]',            'This means the it can be **either one or another**.'),
            ('(*****argument)',    'This means you can have multiple arguments.')
        )

        for name, value in entries: self.embed.add_field(name = name, value = value, inline = False)
        
        self.embed.set_footer(text = f'You were on Page {self.current_page} before this.')
        await self.message.edit(embed = self.embed)
        
        async def go_back_to_current_page():
            await asyncio.sleep(30)
            await self.show_current_page()
        
        self.bot.loop.create_task(go_back_to_current_page())
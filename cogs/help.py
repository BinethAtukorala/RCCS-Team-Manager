import discord
from discord.ext import commands
import asyncio

from lib import utils


class Help(commands.Cog):
    """
    Sends this help message
    """

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def help(self, ctx, *input):
        """Shows details of all the commands of the bot"""

        if not input:
            emb = discord.Embed(title="ℹ  Team Manager - Help",
                                description=f'Use `{self.bot.BOT_PREFIX}help <command>` to gain more information about a command 'f':smiley:\n',
                                color=discord.Color.gold(),)
            
            # TODO: Cogs descriptions

            # cogs_desc = ''
            # for cog in self.bot.cogs:
            #     cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            # emb.add_field(name='Modules', value=cogs_desc, inline=False)

            commands_desc = ""
            for command in self.bot.walk_commands():
                # if not command.cog_name and not command.hidden:
                if not command.hidden:
                    commands_desc += f'`{self.bot.BOT_PREFIX}{command.name}` - {command.help}\n'
            
            # if commands_desc:
            if commands_desc:
                emb.add_field(name="Commands", value=commands_desc, inline=False)
            
            emb.add_field(name="About", value=f"The Team Manager bot is developed by the **RCCS Development Team 2021** *(Avexra#7070, tarithj#7332)*, based on discord.py.\n\n\
                                                Please visit https://github.com/BinethAtukorala/RCCS-Team-Manager to submit ideas or bugs.")
            emb.set_footer(text=f"- Royal College Computer Society '21")
        
        elif len(input) == 1:
            for command in self.walk_commands():
                if (not command.hidden) and command.name == input[0].lower():
                    emb = discord.Embed(title=f'Help - `{self.bot.BOT_PREFIX}{command.name}`',
                                        description=command.help, 
                                        color=discord.Color.gold())
                    break
                else:
                    emb = discord.Embed(title="What's that?!",
                                        description=f"I've never heard form a module called `{input[0]}` before :scream:",
                                        color=discord.Color.gold())       
        
        elif len(input) > 1:
            emb = discord.Embed(title="That's too much.",
                                description="Please request only one module at one :sweat_smile:",
                                color=discord.Color.gold())
        
        await ctx.send(embed=emb)

def setup(bot):
    bot.add_cog(Help(bot))
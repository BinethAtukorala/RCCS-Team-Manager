# ---------- Discord Imports
import discord
from discord.ext import commands

import asyncio
import copy
from datetime import datetime

from lib import utils

INITIAL_EXTENSIONS = [
    'cogs.help',
    'cogs.todo'
]

class TeamManager(commands.Bot):
    def __init__(self, prefix, token):
        self.BOT_PREFIX = prefix
        self.TOKEN = token
        super().__init__(command_prefix=prefix, description="Discord bot for Team Management")
        self.remove_command("help")

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                utils.warn("Failed to load extension {}\n{}: {}".format(
                    extension, type(e).__name__, e
                ))

    async def on_ready(self):
        print("Logged in as:")
        print("Username: " + self.user.name + "#" + self.user.discriminator)
        print("ID: " + str(self.user.id))
        print("------")
        print("Connected to servers: ")
        guilds = await self.fetch_guilds(limit=100).flatten()
        for guild in guilds:
            print("*", guild.name)
        await self.change_presence(status=discord.Status.online, activity=discord.Game("📑 Todo Crunch"))

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)
        ctx = await self.get_context(message)
        if ctx.invoked_with and ctx.invoked_with.lower() not in self.commands and ctx.command is None:
            msg = copy.copy(message)
            if ctx.prefix:
                new_content = msg.content[len(ctx.prefix):]
                msg.content = "{}tag get {}".format(ctx.prefix, new_content)
                await self.process_commands(msg)
    
    
    async def close(self):
        await super().close()
        # await self.session.close()

    def run(self):
        super().run(self.TOKEN, reconnect=True)

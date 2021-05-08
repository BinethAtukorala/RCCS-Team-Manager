from lib.bot import TeamManager
from lib import utils
import os

import asyncio
from datetime import datetime

# -------- Discord inits

if __name__ == '__main__':

    TOKEN, BOT_PREFIX = utils.get_discord_config()

    utils.info("Starting bot...")

    bot = TeamManager(BOT_PREFIX, TOKEN)
    bot.run()
from lib.team_manager import TeamManager
from lib import utils

import asyncio
from datetime import datetime

# -------- Discord inits

TOKEN, BOT_PREFIX = utils.get_discord_config()

if __name__ == '__main__':
    bot = TeamManager(BOT_PREFIX, TOKEN)
    bot.run()
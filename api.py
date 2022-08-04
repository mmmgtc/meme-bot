import aiohttp
import datetime
from datetime import timedelta

from config import MEME_BACKEND
from utils import generate_stats, discord_print_dict


async def get_stats(ctx, mins=43830):
    print("Getting Memes for Stats")
    url = f"{MEME_BACKEND}/museum/memes/"
    from_time = datetime.datetime.now() - timedelta(minutes=mins)
    params = {"created_at__gte": from_time.isoformat()}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            memes_made = await resp.json()
    print("Now Generating Stats")
    message_header = f'**Stats for {mins} minutes**\n\n'
    stats = generate_stats(memes_made)
    await ctx.send(message_header + discord_print_dict(stats))

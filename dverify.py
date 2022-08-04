import aiohttp

from config import MEME_BACKEND, ADMIN_TOKEN

USER_AUTH_CACHE = {}


async def handle_login(ctx):
    user = await check_user_status(ctx)
    if user is not None:
        await ctx.respond(
            f"Your discord account is connected to memes.party\nETH Address: {user['username']}\nKarma: {user['userprofile']['karma']}\n",
            ephemeral=True)
    else:
        await generate_send_login_link(ctx)


async def generate_send_login_link(ctx):
    discord_username = str(ctx.user)
    print('now generating login link')
    url = f"{MEME_BACKEND}/museum/discord/"
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    json = {"discord_username": discord_username}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json, headers=headers) as resp:
            print(resp.status)
            resp_json = await resp.json()
            print(resp_json)

    generated_url = f'https://memes.party/?dverify={resp_json["token"]}'
    await ctx.respond(
        f"Beep boop, I'm the friendly memes.party bot! 👋 🤖 \nBy logging in with the link below the memes you upload to the Gitcoin meme channels will magically be uploaded to memes.party! 🎺 \n{generated_url}\nHappy memeing!",
        ephemeral=True)


async def check_user_status(ctx):
    discord_username = str(ctx.user)
    url = f"{MEME_BACKEND}/museum/discord/"
    headers = {"Authorization": f"Token {ADMIN_TOKEN}"}
    params = {"d_username": discord_username}
    verified = False
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 404:
                verified = True
                user = await resp.json()
    return user if verified else None


async def get_user_token(user):
    discord_username = str(user)
    if discord_username in USER_AUTH_CACHE:
        return USER_AUTH_CACHE[discord_username]
    url = f"{MEME_BACKEND}/museum/botauth/"
    headers = {"Authorization": f"Token {ADMIN_TOKEN}"}
    params = {"d_username": discord_username}
    verified = False
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            if resp.status != 404:
                verified = True
                token = await resp.json()
                USER_AUTH_CACHE[discord_username] = token['auth_token']
    return token['auth_token'] if verified else None

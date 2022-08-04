import discord
from config import DISCORD_TOKEN
from dverify import get_user_token, handle_login
from memes import valid_image_url, handle_image, handle_upvote
from api import get_stats

intents = discord.Intents.default()
intents.message_content = True

# bot = discord.Client(intents=intents)

bot = discord.Bot(intents=intents)

# print(dir(bot))


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(guild_ids=[922715698407563314, 562828676480237578])
async def hello(ctx):
    # print(dir(ctx))
    await ctx.respond("Hello!", ephemeral=True)


@bot.slash_command(guild_ids=[922715698407563314, 562828676480237578],
                   description="Connect your Discord Account to memes.party")
async def login(ctx):
    print(f'Login request from {ctx.user}')
    bot.loop.create_task(handle_login(ctx))


@bot.slash_command(guild_ids=[922715698407563314, 562828676480237578],
                   description="Stats for meme lords")
async def stats(ctx, mins: discord.Option(int,
                                          "Minutes",
                                          min_value=10,
                                          max_value=10000,
                                          default=60)):
    print(f'Login request from {ctx.user}')
    bot.loop.create_task(get_stats(ctx, mins))


@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    # print(f'{message.id} {message.content}')
    if message.author.id == bot.user.id or message.attachments is None:
        return

    for attachment in message.attachments:
        print(attachment.url)
        if valid_image_url(attachment.url):
            print("found image in attachments")
            bot.loop.create_task(handle_image(attachment, message))


@bot.event
async def on_reaction_add(reaction, user):
    # print("some reaction")
    message = reaction.message
    if user != bot.user:
        bot.loop.create_task(handle_upvote(user, message))
        # print("message dir")
        # print(dir(message))
        # print(message.id)
        # print(message.content)

        # print(dir(reaction))
        # # print(user)
        # print(dir(user))
        # if str(reaction.emoji) == "➡️":
        #     #fetch new results from the Spotify API
        #     bot.loop.create_task(handle_upvote(user, message))
        #     # token = await get_user_token(user)
        #     # print(token)
        #     print('user right')
        # if str(reaction.emoji) == "⬅️":
        #     #fetch new results from the Spotify API
        #     print('user left')


bot.run(DISCORD_TOKEN)

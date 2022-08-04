import aiohttp
import aioipfs
import os
import pprint
import asyncio

from dverify import get_user_token

from config import MEME_BACKEND, ADMIN_TOKEN, DEFAULT_TAG, IMG_DIR

MESSAGE_USER_REACTION_CACHE = {
}  # message with 2, meme_id and a list of users who have tried to upvote (either sucesfully or not)


def valid_image_url(url: str):
    image_extensions = [
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'PNG', 'JPG', 'JPEG', 'GIF', 'BMP'
    ]
    for image_extension in image_extensions:
        if url.endswith('.' + image_extension):
            return True
    return False


async def upload_to_ipfs(files, file_hash_dict):
    print('now adding to ipfs')
    client = aioipfs.AsyncIPFS()

    async for added_file in client.add(*files, recursive=True):
        print('Imported file {0}, CID: {1}'.format(added_file['Name'],
                                                   added_file['Hash']))
        file_hash_dict[added_file['Name']] = added_file['Hash']

    await client.close()


async def meme_party_post(image_name, message, file_hash_dict):
    print('now adding to meme_party')
    discord_username = str(message.author)
    url = f"{MEME_BACKEND}/museum/memes/"
    headers = {
        "Authorization": f"Token {ADMIN_TOKEN}",
        "Content-Type": "application/json"
    }
    json = {
        "title": f'{image_name}',
        "meme_lord": f"{discord_username}",
        "description": "",
        "image":
        f"http://139.59.103.146:8080/ipfs/{file_hash_dict[image_name]}",
        "tags": [{
            "name": f"{DEFAULT_TAG}"
        }],
        "discord_username": discord_username
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json, headers=headers) as resp:
            print(resp.status)
            try:
                meme = await resp.json()
            except:
                meme = await resp.text()
                open('erro_log.html', 'w').write(meme)
                return
            logging_fields = ['image', 'id', 'poaster', 'meme_lord']
            meme = {k: meme[k] for k in logging_fields}
            pprint.pprint(meme)
            return resp.status, meme


async def download_image(url: str, images_path: str = ""):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_name = os.path.basename(url)
                with open(images_path, "wb") as f:
                    f.write(await resp.read())


async def handle_image(attachment, message):
    file_hash_dict = {}
    print(f'Processing New Meme From: {message.author}')
    await download_image(attachment.url,
                         os.path.join(IMG_DIR, attachment.filename))
    await upload_to_ipfs([os.path.join(IMG_DIR, attachment.filename)],
                         file_hash_dict)
    upload_status, meme = await meme_party_post(attachment.filename, message,
                                                file_hash_dict)
    if upload_status in [200, 201]:
        await message.add_reaction("✅")
        MESSAGE_USER_REACTION_CACHE[message.id] = {
            "meme_id": meme["id"],
            "upvoters": []
        }
    else:
        await message.add_reaction("❌")
    print(MESSAGE_USER_REACTION_CACHE)


async def handle_upvote(user, message):
    max_times_to_sleep = 3

    while message.id not in MESSAGE_USER_REACTION_CACHE and max_times_to_sleep > 0:
        await asyncio.sleep(10)
        max_times_to_sleep -= 1

    if message.id not in MESSAGE_USER_REACTION_CACHE:
        return

    if str(user) in MESSAGE_USER_REACTION_CACHE[message.id]["upvoters"]:
        return

    user_auth_token = await get_user_token(user)

    if user_auth_token is None:
        return

    print('now handling upvote')

    meme_id = int(MESSAGE_USER_REACTION_CACHE[message.id]["meme_id"])

    url = f"{MEME_BACKEND}/museum/upvote/"
    headers = {
        "Authorization": f"Token {user_auth_token}",
        "Content-Type": "application/json"
    }
    json = {
        "id": meme_id,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json, headers=headers) as resp:
            print(resp.status)
            try:
                meme = await resp.json()
            except:
                meme = await resp.text()
                open('erro_log.html', 'w').write(meme)
                return
            logging_fields = ['image', 'id', 'poaster', 'meme_lord']
            meme = {k: meme[k] for k in logging_fields}
            print(f'upvoted {meme["id"]} on behalf of {user}')
            # pprint.pprint(meme)
            MESSAGE_USER_REACTION_CACHE[message.id]["upvoters"].append(
                str(user))
            print(MESSAGE_USER_REACTION_CACHE)
            return resp.status, meme


# reaction handling
# if message.id is not in cache then asyncio.sleep for upto 3 times

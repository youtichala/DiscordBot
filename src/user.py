import discord
import json
import config
import src.character
import functions.util
import datetime
import random

user_level = None
register_message = None


def get_json(path):
    global user_level
    f = open(path, 'r', encoding='utf-8')
    user_level = json.load(f)
    f.close()


def try_get_user_data(user_id):
    for user_data in user_level:
        if user_data['user_id'] == (int)(user_id):
            return user_data
    return None


def get_user_data(author):
    global user_level
    has_data = False
    for user_data in user_level:
        if user_data['user_id'] == author.id:
            has_data = True
            return user_data

    if has_data == False:
        nick = ''
        if author.nick != None:
            nick = author.nick

        user_data = {'user_id': author.id,
                     'user_name': author.name,
                     'user_nick': nick,
                     'exp': 0,
                     'chat_clock': str(get_current_utc_timestamp()),
                     'avatar': create_avatar_data()}

        user_level.append(user_data)
        return user_data


def add_user_exp(user_data):
    user_data['exp'] += 1


def check_chat_clock(user_data):
    if 'chat_clock' not in user_data:
        avatar = None
        if 'avatar' not in user_data:
            avatar = create_avatar_data()
        else:
            avatar = user_data['avatar']

        user_level.remove(user_data)
        user_data = {'user_id': user_data['user_id'],
                     'user_name': user_data['user_name'],
                     'user_nick': user_data['user_nick'],
                     'exp': user_data['exp'],
                     'chat_clock': str(get_current_utc_timestamp()),
                     'avatar': avatar}
        user_level.append(user_data)

    if get_current_utc_timestamp() - (int)(user_data['chat_clock']) > config.cool_down_time:
        user_data['chat_clock'] = str(get_current_utc_timestamp())
        return True

    return False


def get_current_utc_timestamp():
    current = datetime.datetime.now(datetime.timezone.utc)
    utc_time = current.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = (int)(utc_time.timestamp())
    return utc_timestamp


def create_avatar_data():
    gender = 'male'
    if random.randint(0, 1) == 1:
        gender = 'female'

    hair_style = '0' + str(random.randint(1, 6))
    wear_style = '0' + str(random.randint(1, 6))
    skin = functions.util.color_parse(
        src.character.skin_table[random.randint(0, len(src.character.skin_table)-1)])
    blusher = functions.util.color_parse(
        src.character.blusher_table[random.randint(0, len(src.character.blusher_table)-1)])
    hair = functions.util.color_parse(
        src.character.hair_table[random.randint(0, len(src.character.hair_table)-1)])
    hair_decoration1 = functions.util.color_parse(
        src.character.wear_table[random.randint(0, len(src.character.wear_table)-1)])
    hair_decoration2 = functions.util.color_parse(
        src.character.wear_table[random.randint(0, len(src.character.wear_table)-1)])
    wear_decoration1 = functions.util.color_parse(
        src.character.wear_table[random.randint(0, len(src.character.wear_table)-1)])
    wear_decoration2 = functions.util.color_parse(
        src.character.wear_table[random.randint(0, len(src.character.wear_table)-1)])

    avatar_data = {
        'gender': gender,
        'hair_style': hair_style,
        'wear_style': wear_style,
        'skin_color': skin[0]+','+skin[1]+','+skin[2],
        'blusher_color': blusher[0]+','+blusher[1]+','+blusher[2],
        'hair_color': hair[0]+','+hair[1]+','+hair[2],
        'hair_decoration1_color': hair_decoration1[0]+','+hair_decoration1[1]+','+hair_decoration1[2],
        'hair_decoration2_color': hair_decoration2[0]+','+hair_decoration2[1]+','+hair_decoration2[2],
        'wear_decoration1_color': wear_decoration1[0]+','+wear_decoration1[1]+','+wear_decoration1[2],
        'wear_decoration2_color': wear_decoration2[0]+','+wear_decoration2[1]+','+wear_decoration2[2]}
    return avatar_data


def update_avatar_data(user_data, avatar_data):

    clock = None
    if 'chat_clock' not in user_data:
        clock = str(get_current_utc_timestamp())
    else:
        clock = user_data['chat_clock']

    user_level.remove(user_data)
    user_data = {'user_id': user_data['user_id'],
                 'user_name': user_data['user_name'],
                 'user_nick': user_data['user_nick'],
                 'exp': user_data['exp'],
                 'chat_clock': clock,
                 'avatar': avatar_data}

    user_level.append(user_data)
    return user_data


def save_json(path):
    f = open(path, 'w')
    json.dump(user_level, f, indent=0)


async def try_get_user_setting_message(client, guild):
    global register_message

    register_channel = discord.utils.get(
        guild.channels, name=config.register_channel)

    async for message in register_channel.history(limit=200):
        if message.author == client.user:
            register_message = message
    if register_message == None:
        register_message = await register_channel.send('歡迎**新同學**加入這個群組～很高興看到你！\n** **\n請在這裡設定與修改自己的棋力\n設定好棋力方便找適合的對手下棋，也可以讓活動舉辦更順利\n** **\n**使用方法 - 加入標籤 :**\n** **\n**1級以上須要經過申請與審核**\n** **\n3級點擊下方的 '+config.k3_emoji+' 標籤\n** **\n5級點擊下方的 '+config.k5_emoji+' 標籤\n** **\n7級點擊下方的 '+config.k7_emoji+' 標籤\n** **\n10級點擊下方的 '+config.k10_emoji+' 標籤\n** **\n15級點擊下方的 '+config.k15_emoji+' 標籤\n** **\n20級點擊下方的 '+config.k20_emoji+' 標籤\n** **\n25級點擊下方的 '+config.k25_emoji+' 標籤\n** **\n沒有任何棋力點擊下方的 '+config.k30_emoji+' 標籤\n** **\n如要更動棋力，直接更改標籤就好囉\n重複點擊一樣的圖案可以取消反應\n** **\n*本功能主要是提供給新進的用戶，身上已經有棋力標籤的同學們可以不用理會(~~也可以玩玩看啦~~)*')
        await register_message.add_reaction(config.k3_emoji)
        await register_message.add_reaction(config.k5_emoji)
        await register_message.add_reaction(config.k7_emoji)
        await register_message.add_reaction(config.k10_emoji)
        await register_message.add_reaction(config.k15_emoji)
        await register_message.add_reaction(config.k20_emoji)
        await register_message.add_reaction(config.k25_emoji)
        await register_message.add_reaction(config.k30_emoji)


async def add_roles(client, payload):
    guild = client.get_guild(payload.guild_id)

    user_data = get_user_data(payload.member)
    add_user_exp(user_data)

    if register_message == None:
        await try_get_user_setting_message(client, guild)

    if payload.message_id == register_message.id:
        if payload.emoji.name == config.k1_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k1_emoji[2:-1].split(':')[1]):
            k1_role = discord.utils.get(
                guild.roles, name=config.k1_id)
            if k1_role in payload.member.roles:
                return
            await payload.member.add_roles(k1_role)
        elif payload.emoji.name == config.k3_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k3_emoji[2:-1].split(':')[1]):
            k3_role = discord.utils.get(
                guild.roles, name=config.k3_id)
            if k3_role in payload.member.roles:
                return
            await payload.member.add_roles(k3_role)
        elif payload.emoji.name == config.k5_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k5_emoji[2:-1].split(':')[1]):
            k5_role = discord.utils.get(
                guild.roles, name=config.k5_id)
            if k5_role in payload.member.roles:
                return
            await payload.member.add_roles(k5_role)
        elif payload.emoji.name == config.k7_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k7_emoji[2:-1].split(':')[1]):
            k7_role = discord.utils.get(
                guild.roles, name=config.k7_id)
            if k7_role in payload.member.roles:
                return
            await payload.member.add_roles(k7_role)
        elif payload.emoji.name == config.k10_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k10_emoji[2:-1].split(':')[1]):
            k10_role = discord.utils.get(
                guild.roles, name=config.k10_id)
            if k10_role in payload.member.roles:
                return
            await payload.member.add_roles(k10_role)
        elif payload.emoji.name == config.k15_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k15_emoji[2:-1].split(':')[1]):
            k15_role = discord.utils.get(
                guild.roles, name=config.k15_id)
            if k15_role in payload.member.roles:
                return
            await payload.member.add_roles(k15_role)
        elif payload.emoji.name == config.k20_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k20_emoji[2:-1].split(':')[1]):
            k20_role = discord.utils.get(
                guild.roles, name=config.k20_id)
            if k20_role in payload.member.roles:
                return
            await payload.member.add_roles(k20_role)
        elif payload.emoji.name == config.k25_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k25_emoji[2:-1].split(':')[1]):
            k25_role = discord.utils.get(
                guild.roles, name=config.k25_id)
            if k25_role in payload.member.roles:
                return
            await payload.member.add_roles(k25_role)
        elif payload.emoji.name == config.k30_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k30_emoji[2:-1].split(':')[1]):
            k30_role = discord.utils.get(
                guild.roles, name=config.k30_id)
            if k30_role in payload.member.roles:
                return
            await payload.member.add_roles(k30_role)


async def remove_roles(client, payload):
    guild = client.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    user_data = get_user_data(member)
    add_user_exp(user_data)

    if register_message == None:
        await try_get_user_setting_message(client, guild)

    if payload.message_id == register_message.id:
        if payload.emoji.name == config.k1_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k1_emoji[2:-1].split(':')[1]):
            k1_role = discord.utils.get(guild.roles, name=config.k1_id)
            if member.roles == None:
                return
            if not k1_role in member.roles:
                return
            await member.remove_roles(k1_role)
        elif payload.emoji.name == config.k3_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k3_emoji[2:-1].split(':')[1]):
            k3_role = discord.utils.get(guild.roles, name=config.k3_id)
            if member.roles == None:
                return
            if not k3_role in member.roles:
                return
            await member.remove_roles(k3_role)
        elif payload.emoji.name == config.k5_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k5_emoji[2:-1].split(':')[1]):
            k5_role = discord.utils.get(guild.roles, name=config.k5_id)
            if member.roles == None:
                return
            if not k5_role in member.roles:
                return
            await member.remove_roles(k5_role)
        elif payload.emoji.name == config.k7_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k7_emoji[2:-1].split(':')[1]):
            k7_role = discord.utils.get(guild.roles, name=config.k7_id)
            if member.roles == None:
                return
            if not k7_role in member.roles:
                return
            await member.remove_roles(k7_role)
        elif payload.emoji.name == config.k10_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k10_emoji[2:-1].split(':')[1]):
            k10_role = discord.utils.get(guild.roles, name=config.k10_id)
            if member.roles == None:
                return
            if not k10_role in member.roles:
                return
            await member.remove_roles(k10_role)
        elif payload.emoji.name == config.k15_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k15_emoji[2:-1].split(':')[1]):
            k15_role = discord.utils.get(guild.roles, name=config.k15_id)
            if member.roles == None:
                return
            if not k15_role in member.roles:
                return
            await member.remove_roles(k15_role)
        elif payload.emoji.name == config.k20_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k20_emoji[2:-1].split(':')[1]):
            k20_role = discord.utils.get(guild.roles, name=config.k20_id)
            if member.roles == None:
                return
            if not k20_role in member.roles:
                return
            await member.remove_roles(k20_role)
        elif payload.emoji.name == config.k25_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k25_emoji[2:-1].split(':')[1]):
            k25_role = discord.utils.get(guild.roles, name=config.k25_id)
            if member.roles == None:
                return
            if not k25_role in member.roles:
                return
            await member.remove_roles(k25_role)
        elif payload.emoji.name == config.k30_emoji[2:-1].split(':')[0] and payload.emoji.id == (int)(config.k30_emoji[2:-1].split(':')[1]):
            k30_role = discord.utils.get(guild.roles, name=config.k30_id)
            if member.roles == None:
                return
            if not k30_role in member.roles:
                return
            await member.remove_roles(k30_role)

# encoding: utf-8
import discord
import src.user
import src.story
import src.chat
import src.join
import src.ogs
import src.tsume
import src.character
import src.competition
import functions.util
import time
from bot_token import key, owner
import config

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)

src.ogs.get_json(config.ogs_path)
src.user.get_json(config.user_level_path)
src.chat.get_json(config.chat_path)
src.story.get_json(config.story_path)
src.competition.get_json(config.competition_path,
                         config.competition_announcement_path,
                         config.competition_ban_path)


def update_user_data(message):
    user_data = src.user.get_user_data(message.author)
    if src.user.check_chat_clock(user_data):
        src.user.add_user_exp(user_data)


async def chat_action(message, msgs):
    if len(msgs) > 1:
        target_chat, key = src.chat.get_target_chatdata(msgs[1])
        if target_chat != None:
            if src.chat.get_delete_condiction(target_chat):
                await message.delete()
            if key != None:
                responces, speed, method = src.chat.get_respone(
                    target_chat, key)
            else:
                responces, speed, method = src.chat.get_respone(
                    target_chat, message)

            if responces != None:
                new_msg = None
                for responce in responces:
                    if method == 'send':
                        if new_msg != None:
                            await new_msg.delete()

                        new_msg = await message.channel.send(responce)
                    elif method == 'reply':
                        if new_msg != None:
                            await new_msg.delete()

                        new_msg = await message.reply(responce)
                    else:
                        break
                    time.sleep(speed)
                return True
        else:
            if message.author.id != owner:
                await message.reply('我聽不懂你的問題，可以教教我嗎?')
                return True
            else:
                return False
    else:
        return False


async def competition_action(message, msgs):
    return await src.competition.competition_action(client, message, msgs)


async def tsume_action(message, msgs):
    return await src.tsume.tsume_action(message, msgs)


async def ogs_action(message, msgs):
    return await src.ogs.ogs_action(client, message, msgs)


async def character_action(message, msgs):
    return await src.character.character_action(message, msgs)


async def story_action(message, msgs):
    if message.author.id == owner:
        msg = src.story.get_value(msgs[1])
        if msg == None:
            return False
        else:
            await message.delete()
            await message.channel.send(content=msg)
            return True
    else:
        return False


@client.event
async def on_ready():
    print('目前登入身份：', client.user)


@client.event
async def on_member_join(member):
    await src.join.show_welcome(member, config.entrance_channel, config.register_channel)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        update_user_data(message)
        msgs = functions.util.str_split(message.content, ' ')
        if len(msgs) > 1:
            if msgs[0] == config.prefix:
                if message.author.id == owner and msgs[1] == '結束並存檔':
                    src.user.save_json(config.user_level_path)
                    src.competition.save_json(
                        config.competition_path, config.competition_ban_path)
                    src.ogs.save_json(config.ogs_path)
                    await message.channel.send('大家晚安 (๑ơ ₃ ơ)♥~')
                    await client.close()
                elif await tsume_action(message, msgs) == False:
                    if await ogs_action(message, msgs) == False:
                        if await story_action(message, msgs) == False:
                            if await character_action(message, msgs) == False:
                                await chat_action(message, msgs)
            elif msgs[0] == config.score_prefix:
                await competition_action(message, msgs)


@client.event
async def on_raw_reaction_add(payload):
    if payload.user_id != client.user.id:
        await src.user.add_roles(client, payload)


@client.event
async def on_raw_reaction_remove(payload):
    if payload.user_id != client.user.id:
        await src.user.remove_roles(client, payload)


@client.event
async def on_interaction(interaction):
    await src.competition.handle_interaction_key(interaction, interaction.data['custom_id'])

client.run(key)
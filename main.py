import discord
import src.user
import src.chat
import src.join
import functions.util
from bot_token import key
from config import entrance_channel, register_channel, user_level_path, chat_path, prefix

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

src.user.get_json(user_level_path)
src.chat.get_json(chat_path)

@client.event
async def on_ready():
    print('目前登入身份：', client.user)

@client.event
async def on_member_join(member):
    await src.join.show_welcome(member, entrance_channel, register_channel)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else :
        msgs =  functions.util.str_split(message.content,' ')

        if len(msgs) > 1 :
            if msgs[0] == prefix :
                user_data = src.user.get_user_data(message.author,)
                src.user.add_user_exp(user_data)

                target_chat, key = src.chat.get_target_chatdata(msgs[1])
                if target_chat != None :
                    if src.chat.get_delete_condiction(target_chat) :
                        await message.delete()
                    if key != None :
                        responce = src.chat.get_respone(target_chat, key)
                    else :
                        responce = src.chat.get_respone(target_chat, message)

                    if responce != None :
                        await message.channel.send(responce)

try:
    client.run(key)
finally:
    src.user.save_json(user_level_path)
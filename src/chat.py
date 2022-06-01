import discord
import json
import random
import functions.util
import datetime
import re

chat = None

def get_json(path):
    global chat
    f = open(path, 'r', encoding='utf-8')
    chat = json.load(f)
    f.close()

def get_target_chatdata(message):
    for chat_data in chat:
        for key in chat_data['key']:
            if re.search(key, message) != None :
                if len(re.search(key, message).groups()) > 1:
                    return chat_data, re.search(key, message).group(1)
                else :
                    return chat_data, None
    return None, None

def get_delete_condiction(chatdata):
    if chatdata != None : 
        return chatdata['delete_msg']
    return False

def get_responce_condiction(chatdata):
    if chatdata != None : 
        return functions.util.str_split(chatdata['condiction'],'|')
    return None

def get_responce_max_count(chatdata):
    if chatdata != None : 
        return chatdata['max_count']
    return -1

def is_proper_time(chatdata):
    current = datetime.datetime.now().hour
    if chatdata != None : 
        active_times = chatdata['active_time']
        for period in active_times :
            keys = functions.util.str_split(period,'-')
            if current >= int(keys[0]) and current < int(keys[1]) :
                return True
        return False
    return False


def get_respone(chatdata, value):
    if chatdata != None : 
        max_count = get_responce_max_count(chatdata)

        if max_count > 0 :
            chatdata['max_count'] -= 1
        elif max_count == 0 :
            return chatdata['error'][random.randint(0,len(chatdata['error'])-1)]

        if len(chatdata['responce']) > 0 :
            condictions = get_responce_condiction(chatdata)
            msg = ''

            if 'Time' in condictions :
                if not is_proper_time(chatdata) :
                    return chatdata['error'][random.randint(0,len(chatdata['error'])-1)]

            if 'Random' in condictions :
                msg = chatdata['responce'][random.randint(0,len(chatdata['responce'])-1)]
            else :
                msg = chatdata['responce'][0]

            key = functions.util.get_key(msg)
            if key != None:
                return functions.util.str_replace(msg, key, functions.util.get_replace_value(key, value))
            else :
                return msg
        else :
            return None
    return None

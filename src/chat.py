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
            if re.search(key, message):
                if len(re.search(key, message).groups()) > 0:
                    return chat_data, re.search(key, message).group(1)
                else:
                    return chat_data, None
    return None, None


def get_delete_condiction(chatdata):
    if chatdata != None:
        return chatdata['delete_msg']
    return False


def get_speed(chatdata):
    if chatdata != None:
        return chatdata['speed']
    return 0


def get_selector(chatdata):
    if chatdata != None:
        return functions.util.str_split(chatdata['selector'], '|')
    return None


def get_method(chatdata):
    if chatdata != None:
        return chatdata['method']
    return False


def get_responce_max_count(chatdata):
    if chatdata != None:
        return chatdata['max_count']
    return -1


def is_proper_time(chatdata):
    current = datetime.datetime.now().astimezone(
        datetime.timezone(datetime.timedelta(hours=8))).hour
    print(current)
    if chatdata != None:
        active_times = chatdata['active_time']
        for period in active_times:
            keys = functions.util.str_split(period, '-')
            if current >= int(keys[0]) and current < int(keys[1]):
                return True
        return False
    return False


def get_respone(chatdata, value):
    if chatdata != None:
        max_count = get_responce_max_count(chatdata)

        if max_count > 0:
            chatdata['max_count'] -= 1
        elif max_count == 0:
            return [chatdata['error'][random.randint(0, len(chatdata['error'])-1)]], 1

        if len(chatdata['responce']) > 0:
            selectors = get_selector(chatdata)
            index = 0
            responce = ''

            speed = get_speed(chatdata)
            method = get_method(chatdata)

            if 'Time' in selectors:
                if not is_proper_time(chatdata):
                    return [chatdata['error'][random.randint(0, len(chatdata['error'])-1)]+"現在是 " + str(datetime.datetime.now(datetime.timezone.utc).hour + 8) + " 點"], 1, method

            if 'Random' in selectors:
                index = random.randint(0, len(chatdata['responce'])-1)

            responce = chatdata['responce'][index]

            msgs = functions.util.str_split(responce, '|')

            key = functions.util.get_key(msgs[0])
            if key != None:
                replace_value = functions.util.get_replace_value(key, value)
                msgs = [functions.util.str_replace(
                    msg, key, replace_value) for msg in msgs]
                return msgs, speed, method
            else:
                return msgs, speed, method
        else:
            return None, 1, method
    return None, 1, method

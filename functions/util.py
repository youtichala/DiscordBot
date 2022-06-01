import re

def str_replace(msg, key, value):
    if msg != None :
        return msg.replace(key, value)
    else :
        return None

def str_split(msg, key):
    if msg != None :
        return msg.split(key)
    else :
        return None

def get_key(msg):
    if msg != None :
        if re.search("{.*}", msg) != None :
            return re.search("{.*}", msg).group()
        else :
            return None
    else :
        return None

def get_replace_value(key, value):
    replace_key = ''

    if(value != None) :
        if key == '{Name}' :
            replace_key = f'<@{value.author.id}>'
        elif key == '{Channel}' :
            replace_key = f'<#{value.channel.id}>'
        elif key == '{Guild}' :
            replace_key = '**'+value.guild.name+'**'
        elif key == '{Key}' :
            replace_key = value

    return replace_key
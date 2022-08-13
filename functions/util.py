import re


def str_replace(msg, key, value):
    if msg != None:
        return msg.replace(key, value)
    else:
        return None


def str_split(msg, key):
    if msg != None:
        return msg.split(key)
    else:
        return None


hexadecimal_table = ['0', '1', '2', '3', '4', '5',
                     '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', ]


def color_parse(msg: str):
    if msg != None:
        if msg.startswith('#'):
            msg = msg[1::]

            color_r = hexadecimal_table.index(
                msg[0].upper())*15 + hexadecimal_table.index(msg[1].upper())

            color_g = hexadecimal_table.index(
                msg[2].upper())*15 + hexadecimal_table.index(msg[3].upper())

            color_b = hexadecimal_table.index(
                msg[4].upper())*15 + hexadecimal_table.index(msg[5].upper())

            return [str(color_r), str(color_g), str(color_b)]
        else:
            return None
    else:
        return None


def get_key(msg):
    if msg != None:
        if re.search("{.*}", msg) != None:
            return re.search("{.*}", msg).group()
        else:
            return None
    else:
        return None


def get_ogs_game_id(url):
    if url != None:
        if re.findall("online-go.com/game/([0-9]{0,10})", url):
            return re.findall("online-go.com/game/([0-9]{0,10})", url)[0]
        else:
            return None
    else:
        return None


def get_time(msg):  # 2022-07-10T09:29:39.489875-04:00
    if msg != None:
        if re.findall("([0-9]{1,6})[-|T|:|.]", msg):
            # [2022,07,10,09,29,39,489875,04]
            return re.findall("([0-9]{1,6})[-|T|:|.]", msg)
        else:
            return None
    else:
        return None


def get_replace_value(key, value):
    replace_key = ''

    if(value != None):
        if key == '{Name}':
            replace_key = f'<@{value.author.id}>'
        elif key == '{Channel}':
            replace_key = f'<#{value.channel.id}>'
        elif key == '{Guild}':
            replace_key = '**'+value.guild.name+'**'
        elif key == '{Key}':
            replace_key = value

    return replace_key

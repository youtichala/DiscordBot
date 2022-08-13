import discord
import json
import time
import src.request
import src.user
import functions.util
import bot_token

ogs = None


def get_json(path):
    global ogs
    f = open(path, 'r', encoding='utf-8')
    ogs = json.load(f)
    f.close()


async def ogs_action(client, message, msgs):
    if len(msgs) == 4:
        if msgs[1] == "OGS綁定":
            if message.author.id == bot_token.owner:
                user_id = msgs[2][2:-1]
                if src.user.try_get_user_data(user_id) == None:
                    await message.reply('用戶尚未登記帳號')
                else:
                    if add_ogs_data(user_id, msgs[3]) == None:
                        await message.reply('用戶資料已存在')
                    else:
                        await message.reply("綁定成功")
                return True
            else:
                await message.reply('這是管理員專屬指令喔 ~ 如果需要綁定OGS帳號請洽 <@'+str(bot_token.owner)+'>')
                return True
        else:
            return False
    else:
        return False


def try_find_user_data_by_user(author):
    for user in ogs:
        if author.id == user['user_id']:
            return user
    return None


def try_find_user_data_by_id(ogs_id):
    for user in ogs:
        if ogs_id == user['ogs_id'][0]:
            return user
    return None


def add_ogs_data(user_id, ogs_id):
    global ogs
    user_ogs_data = None

    for ogs_data in ogs:
        if ogs_data['user_id'] == (int)(user_id):
            user_ogs_data = ogs_data

    if user_ogs_data != None:
        if (int)(ogs_id) not in user_ogs_data['ogs_id']:
            user_ogs_data['ogs_id'].append((int)(ogs_id))
        else:
            return None
    else:
        user_ogs_data = {'user_id': (int)(user_id), 'ogs_id': [(int)(ogs_id)]}
        ogs.append(user_ogs_data)

    return user_ogs_data


def get_ogs_gamer_data(user_id):
    return src.request.get_gamer_data(user_id)


def get_ogs_game_data(game_id):
    return src.request.get_games_data(game_id)


def invite_user_to_game(user_name, game_id):
    return src.request.invite_menber_to_tournaments(user_name, game_id)


def valid_game_data(result, can_be_tournament, event_start_time_hour, event_end_time_hour):

    time_elements = functions.util.get_time(result['started'])
    time_in_hour = int(time_elements[0]) * 365 + \
        int(time_elements[1]) * 30 + int(time_elements[2])
    time_in_hour = time_in_hour * 24 + int(time_elements[3]) + 12

    if time_in_hour < event_start_time_hour:
        return False, '比賽時間錯誤，該比賽比活動時間早開始'

    if time_in_hour > event_end_time_hour:
        return False, '比賽時間錯誤，該比賽比活動時間晚開始'

    if result['width'] != 19:
        return False, '棋盤大小錯誤，應該要是19 X 19'

    if result['height'] != 19:
        return False, '棋盤大小錯誤，應該要是19 X 19'

    if result['komi'] != "7.50":
        return False, '貼目錯誤，應該要是三又四分之三子'

    if result['handicap'] != 0:
        return False, '比賽不允許讓子'

    if result['disable_analysis'] != True:
        return False, '比賽不允許預測落子和分析功能'

    if result['rules'] != 'chinese':
        return False, '規則錯誤，應該要是中國規則'

    time_control = json.loads(result['time_control_parameters'])

    if time_control['system'] != 'byoyomi':
        return False, '時間控制設定錯誤，應該要是讀秒制'

    if time_control['time_control'] != 'byoyomi':
        return False, '時間控制設定錯誤，應該要是讀秒制'

    if time_control['speed'] != 'live':
        return False, '對局速度設定錯誤，應該要是即時'

    if time_control['main_time'] != 600:
        return False, '基本時間設定錯誤，應該要是10分鐘'

    if time_control['period_time'] != 30:
        return False, '每週期時間設定錯誤，應該要是30秒'

    if time_control['periods'] != 3:
        return False, '週期數設定錯誤，應該要是3次'

    if result['annulled'] != False:
        return False, '未完賽'

    if not can_be_tournament:
        if result['tournament'] != None:
            return False, '本活動僅接受自由對局，不含錦標賽'

    return True, '比賽合法'


def get_game_result(result):

    win_lost = 2

    if result['white_lost'] == True:
        win_lost = 0

    if result['black_lost'] == True:
        win_lost = 1

    if win_lost == 2:
        return 2, '平局'

    msg = ''

    if 'Resignation' in result['outcome']:
        msg = '投降'
    elif 'Timeout' in result['outcome']:
        msg = '超時'
    else:
        msg = result['outcome'].replace(' points', '')

    if win_lost == 0:
        return 0, msg

    if win_lost == 1:
        return 1, msg


async def serialize_game_date(message, game_id, can_be_tournament, start_time, end_time):
    new_msg = await message.reply('正在檢查比賽資訊...')
    result = get_ogs_game_data(game_id)
    if result == None:
        await new_msg.edit(content='讀取失敗，比賽連結錯誤')
        return new_msg, -1, -1, -1, -1, 0

    event_start_time_hour = start_time[0] * \
        365 + start_time[1] * 30 + start_time[2]
    event_start_time_hour = event_start_time_hour * 24 + start_time[3]

    event_end_time_hour = end_time[0] * 365 + end_time[1] * 30 + end_time[2]
    event_end_time_hour = event_end_time_hour * 24 + end_time[3]

    is_valid, msg = valid_game_data(
        result, can_be_tournament, event_start_time_hour, event_end_time_hour)
    time.sleep(1)
    if is_valid == False:
        await new_msg.edit(content=msg)
        return new_msg, -1, -1, -1, -1, 0
    else:
        await new_msg.edit(content='比賽規則設定正常，正在檢查成績中...')
        result_type, ways_to_win = get_game_result(result)
        time.sleep(1)
        return new_msg, result_type, ways_to_win, result['black'], result['white'], len(result['gamedata']['moves'])


def save_json(path):
    f = open(path, 'w')
    json.dump(ogs, f, indent=0)

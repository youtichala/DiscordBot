import discord
from discord.ui import Button,  View
import json
import src.ogs
import config
import time
import random
import functions.util
import bot_token
import datetime

competition = None
competition_ban = None
competition_announcement = None
register_message = None
leaderboard_message = None
announcement_channel = None
rank_table = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


def get_json(path, announcement_path, ban_path):
    global competition, competition_announcement, competition_ban
    f = open(path, 'r', encoding='utf-8')
    competition = json.load(f)
    f.close()

    f = open(announcement_path, 'r', encoding='utf-8')
    competition_announcement = json.load(f)
    f.close()

    f = open(ban_path, 'r', encoding='utf-8')
    competition_ban = json.load(f)
    f.close()


def try_find_user_data_by_ogs(ogs_id):
    for user in competition:
        if int(ogs_id) == user['ogs_id']:
            return user
    return None


def try_find_user_data_by_id(user_id):
    for user in competition:
        if int(user_id) == user['user_id']:
            return user
    return None


def remove_user_data(user_id):
    data = None
    for user in competition:
        if int(user_id) == user['user_id']:
            data = user

    if data != None:
        competition.remove(data)


async def competition_action(client, message, msgs):
    global competition_ban
    if len(msgs) > 2:
        if msgs[1] == "登記" or msgs[1] == "自由賽":
            if str(message.author.id) in competition_ban:
                await message.channel.send(f'<@{message.author.id}> 你已經被管理員手動禁止了，如果有問題請洽<@{bot_token.owner}>')
                return

            can_be_tournament = False
            game_id = pharse_ogs_url(msgs[2])
            reply_msg, result_type, ways_to_win, black_player, white_player, moves = await src.ogs.serialize_game_date(message, game_id, can_be_tournament, [2021, 8, 1, 0], [2022, 8, 30, 21])

            if result_type != -1:
                if await create_outcome_msg(reply_msg, result_type, ways_to_win, black_player, white_player):
                    time.sleep(2)
                    score, bang_win, bang_loss = await calculate_score(client, reply_msg, game_id, 'free', result_type, black_player, white_player)

                    if score != -1:
                        await trigger_event(event_phaser(result_type, ways_to_win, moves,
                                                         black_player, white_player, bang_win, bang_loss, score), message.guild)
            else:
                user_osg_data = src.ogs.try_find_user_data_by_user(
                    message.author)
                if not user_osg_data == None:
                    user_win_data = try_find_user_data_by_ogs(
                        user_osg_data['ogs_id'][0])
                    if not user_win_data == None:
                        user_win_data['error'] += 1
                        if user_win_data['error'] >= 5 and not 'error_too_many' in user_win_data['event_history']:
                            user_win_data['event_history'].append(
                                'error_too_many')
                            await trigger_event([('error_too_many', user_win_data)], message.guild)

            return True
        elif msgs[1] == "固定賽":
            if message.author.id == bot_token.owner:
                can_be_tournament = True
                game_id = pharse_ogs_url(msgs[2])
                reply_msg, result_type, ways_to_win, black_player, white_player, moves = await src.ogs.serialize_game_date(message, game_id, can_be_tournament, [2021, 8, 1, 0], [2022, 8, 30, 21])

                if result_type != -1:
                    if await create_outcome_msg(reply_msg, result_type, ways_to_win, black_player, white_player):
                        time.sleep(2)
                        score, bang_win, bang_loss = await calculate_score(client, reply_msg, game_id, 'fixed', result_type, black_player, white_player)

                        if score != -1:
                            await trigger_event(event_phaser(result_type, ways_to_win, moves,
                                                             black_player, white_player, bang_win, bang_loss, score), message.guild)
                return True
        elif msgs[1] == "AI":
            if message.author.id == bot_token.owner:
                new_msg = await message.reply('正在檢查比賽資訊...')
                score = await calculate_ai_score(client, new_msg, 'free', msgs[2][2:-1], msgs[3])
                if score != -1:
                    await trigger_event(event_ai_phaser(msgs[2][2:-1], score), message.guild)
                return True
        elif msgs[1] == "鎖定":
            if message.author.id == bot_token.owner:
                user_id = msgs[2][2:-1]
                if user_id not in competition_ban:
                    competition_ban.append(user_id)
                remove_user_data(user_id)
                await message.reply('成員<@'+user_id+'>已鎖定')

            if leaderboard_message == None:
                await try_get_user_leaderboard_message(client, message.guild)
            else:
                await leaderboard_message.edit(content=create_leaderboard_msg())
        elif msgs[1] == "黑APP":
            if message.author.id == bot_token.owner:
                new_msg = await message.reply('正在檢查比賽資訊...')
                score = await calculate_app_score(client, new_msg, 'free', int(msgs[4]), msgs[2][2:-1], msgs[3][2:-1])
                if score != -1:
                    await trigger_event(event_ai_phaser(msgs[2][2:-1], score), message.guild)
                return True
        else:
            return False
    elif len(msgs) > 1:
        if msgs[1] == "控制板":
            if message.author.id == bot_token.owner:
                await create_control_panel(message)
                return True
        elif msgs[1] == "使用說明":
            if message.author.id == bot_token.owner:
                await create_tutorial(message)
                return True
        elif msgs[1] == "排行榜":
            if message.author.id == bot_token.owner:
                await create_leaderboard(client, message)
                return True
        else:
            return False
    else:
        return False


def pharse_ogs_url(url):
    if 'game' in url:
        return functions.util.get_ogs_game_id(url)
    else:
        return url


async def create_leaderboard(client, message):
    if leaderboard_message == None:
        await try_get_user_leaderboard_message(client, message.guild)
    else:
        await leaderboard_message.edit(content=create_leaderboard_msg())

    await message.delete()


async def create_tutorial(message):
    competition_record_id = discord.utils.get(
        message.guild.channels, name=config.competition_record_channel).id
    competition_register_id = discord.utils.get(
        message.guild.channels, name=config.competition_register_channel).id
    await message.channel.send(content=f'◆ 報名或看自己的戰績排名請到 <#{competition_register_id}>\n** **\n        報名：點擊 **報名活動** 按鈕\n** **\n        查看自己的分數與戰績：點擊 **查詢戰績** 按鈕\n** **\n        查看自己的對戰歷史清單：點擊 **對戰紀錄** 按鈕\n** **\n◆ 登記比賽結果請到 <#{competition_record_id}>\n** **\n        登記比賽：積分賽 登記 [比賽編號/比賽網址]\n        *ps : 比賽編號為，OGS對弈頁面網址最後面的號碼*\n** **\n', file=discord.File(config.get_root_path() + 'img/ogs_info.png'))
    await message.delete()


async def create_control_panel(message):
    global register_channel
    register_button = Button(
        label="報名活動", custom_id='competition_register', style=discord.ButtonStyle.gray)
    rank_button = Button(
        label="查詢戰績", custom_id='competition_self_rank', style=discord.ButtonStyle.gray)
    history_button = Button(
        label="對戰紀錄", custom_id='competition_history', style=discord.ButtonStyle.gray)

    view = View(timeout=None)
    view.add_item(register_button)
    view.add_item(rank_button)
    view.add_item(history_button)

    await message.delete()
    await message.channel.send(content=f'**小漁村組分組積分賽** (棋力限制: 10級(含)以下)\n報名時間 : 8/1 ~ 8/5\n自由賽比賽時間 : 8/1 ~ 8/30\n固定賽比賽時間 : 8/6 ~ 8/30\n結算時間 : 8/31', view=view)
    register_channel = await message.channel.send('當前參賽者人數 ： '+str(len(competition)))


async def handle_interaction_key(interaction, key):
    if key == 'competition_register':
        await register(interaction)
    elif key == 'competition_self_rank':
        await rank(interaction)
    elif key == 'competition_history':
        await history(interaction)


async def calculate_score(client, message, game_id, battle_type, result, black_player, white_player):
    bang_win = False
    bang_loss = False
    black_data = try_find_user_data_by_ogs(black_player)
    white_data = try_find_user_data_by_ogs(white_player)

    rounds = 0
    rounds = add_competition_record(
        game_id, battle_type, result == 0 or result == 2, black_data, white_data)

    if rounds == -1:
        await message.edit(content='分數更新失敗，比賽已經登記過瞜')
        return -1, False, False

    rounds = add_competition_record(
        game_id, battle_type, result == 1 or result == 2, white_data, black_data)

    if rounds == -1:
        await message.edit(content='分數更新失敗，比賽已經登記過瞜')
        return -1, False, False

    msg = ''
    if battle_type == 'free':
        msg = '雙方是第 '+str(rounds)+' 次對弈\n'

    score = 0
    if result == 0:  # 黑勝
        white_data[battle_type]['total_run'] += 1
        black_data[battle_type]['total_run'] += 1

        if black_data[battle_type]['combo'] < 0:
            if black_data[battle_type]['combo'] < -3:
                bang_win = True
            black_data[battle_type]['combo'] = 1
        else:
            black_data[battle_type]['combo'] += 1

        if white_data[battle_type]['combo'] > 0:
            if white_data[battle_type]['combo'] > 3:
                bang_loss = True
            white_data[battle_type]['combo'] = -1
        else:
            white_data[battle_type]['combo'] -= 1

        score = add_competition_score(
            battle_type, black_data['free']['total_run'], rounds)
        black_data['score'] += score

        await message.edit(content='分數已更新，黑方勝：\n' +
                           '黑方：<@'+str(black_data['user_id'])+'> 完成第 '+str(black_data[battle_type]['total_run'])+' 場比賽\n' +
                           '白方：<@'+str(white_data['user_id'])+'> 完成第 '+str(white_data[battle_type]['total_run'])+' 場比賽\n' +
                           msg + '黑方積分增加' + str(score) + ' 分，當前總分為 '+str(black_data['score'])+' 分')

    elif result == 1:  # 白勝
        black_data[battle_type]['total_run'] += 1
        white_data[battle_type]['total_run'] += 1

        if white_data[battle_type]['combo'] < 0:
            if white_data[battle_type]['combo'] < -3:
                bang_win = True
            white_data[battle_type]['combo'] = 1
        else:
            white_data[battle_type]['combo'] += 1

        if black_data[battle_type]['combo'] > 0:
            if black_data[battle_type]['combo'] > 3:
                bang_loss = True
            black_data[battle_type]['combo'] = -1
        else:
            black_data[battle_type]['combo'] -= 1

        score = add_competition_score(
            battle_type, white_data['free']['total_run'], rounds)
        white_data['score'] += score

        await message.edit(content='分數已更新，白方勝：\n' +
                           '黑方：<@'+str(black_data['user_id'])+'> 完成第 '+str(black_data[battle_type]['total_run'])+' 場比賽\n' +
                           '白方：<@'+str(white_data['user_id'])+'> 完成第 '+str(white_data[battle_type]['total_run'])+' 場比賽\n' +
                           msg + '白方積分增加' + str(score) + ' 分，當前總分為 '+str(white_data['score'])+' 分')

    elif result == 2:  # 平手
        black_data[battle_type]['total_run'] += 1

        if black_data[battle_type]['combo'] < 0:
            if black_data[battle_type]['combo'] < -3:
                bang_win = True
            black_data[battle_type]['combo'] = 1
        else:
            black_data[battle_type]['combo'] += 1

        if white_data[battle_type]['combo'] < 0:
            if white_data[battle_type]['combo'] < -3:
                bang_win = True
            white_data[battle_type]['combo'] = 1
        else:
            white_data[battle_type]['combo'] += 1

        score = add_competition_score(
            battle_type, black_data['free']['total_run'], rounds)
        black_data['score'] += score

        white_data[battle_type]['total_run'] += 1
        score = add_competition_score(
            battle_type, white_data['free']['total_run'], rounds)
        white_data['score'] += score

        await message.edit(content='分數已更新，平手：\n' +
                           '黑方：<@'+str(black_data['user_id'])+'> 完成第 '+str(black_data[battle_type]['total_run'])+' 場比賽\n' +
                           '白方：<@'+str(white_data['user_id'])+'> 完成第 '+str(white_data[battle_type]['total_run'])+' 場比賽\n' +
                           msg + '雙方積分增加' + str(score) + ' 分')

    if leaderboard_message == None:
        await try_get_user_leaderboard_message(client, message.guild)
    else:
        await leaderboard_message.edit(content=create_leaderboard_msg())

    return score, bang_win, bang_loss


async def calculate_ai_score(client, message, battle_type, player_id, adversary_name):
    player_data = try_find_user_data_by_id(player_id)
    rounds = 0

    rounds = add_ai_competition_record(
        battle_type, player_data, adversary_name)

    msg = ''
    if battle_type == 'free':
        msg = '雙方是第 '+str(rounds)+' 次對弈\n'

    score = 0

    player_data[battle_type]['total_run'] += 1

    score = add_competition_score(
        battle_type, player_data['free']['total_run'], rounds)
    player_data['score'] += score

    await message.edit(content='分數已更新：\n' +
                       '<@'+str(player_data['user_id'])+'> 完成第 '+str(player_data[battle_type]['total_run'])+' 場比賽\n' +
                       msg + '積分增加' + str(score) + ' 分，當前總分為 '+str(player_data['score'])+' 分')

    if leaderboard_message == None:
        await try_get_user_leaderboard_message(client, message.guild)
    else:
        await leaderboard_message.edit(content=create_leaderboard_msg())

    return score


async def calculate_app_score(client, message, battle_type, result, black_id, white_id):
    black_data = try_find_user_data_by_id(black_id)
    white_data = try_find_user_data_by_id(white_id)

    rounds = 0
    rounds = add_app_competition_record(
        battle_type, result == 0 or result == 2, black_data, white_data)

    if rounds == -1:
        await message.edit(content='分數更新失敗，比賽已經登記過瞜')
        return -1

    rounds = add_app_competition_record(
        battle_type, result == 1 or result == 2, white_data, black_data)

    if rounds == -1:
        await message.edit(content='分數更新失敗，比賽已經登記過瞜')
        return -1
    msg = ''
    if battle_type == 'free':
        msg = '雙方是第 '+str(rounds)+' 次對弈\n'

    score = 0
    if result == 0:  # 黑勝
        white_data[battle_type]['total_run'] += 1
        black_data[battle_type]['total_run'] += 1

        if black_data[battle_type]['combo'] < 0:
            black_data[battle_type]['combo'] = 1
        else:
            black_data[battle_type]['combo'] += 1

        if white_data[battle_type]['combo'] > 0:
            white_data[battle_type]['combo'] = -1
        else:
            white_data[battle_type]['combo'] -= 1

        score = add_competition_score(
            battle_type, black_data['free']['total_run'], rounds)
        black_data['score'] += score
        print(rounds)
        print(score)
        await message.edit(content='分數已更新，黑方勝：\n' +
                           '黑方：<@'+str(black_data['user_id'])+'> 完成第 '+str(black_data[battle_type]['total_run'])+' 場比賽\n' +
                           '白方：<@'+str(white_data['user_id'])+'> 完成第 '+str(white_data[battle_type]['total_run'])+' 場比賽\n' +
                           msg + '黑方積分增加' + str(score) + ' 分，當前總分為 '+str(black_data['score'])+' 分')

    elif result == 1:  # 白勝
        black_data[battle_type]['total_run'] += 1
        white_data[battle_type]['total_run'] += 1

        if white_data[battle_type]['combo'] < 0:
            white_data[battle_type]['combo'] = 1
        else:
            white_data[battle_type]['combo'] += 1

        if black_data[battle_type]['combo'] > 0:
            black_data[battle_type]['combo'] = -1
        else:
            black_data[battle_type]['combo'] -= 1

        score = add_competition_score(
            battle_type, white_data['free']['total_run'], rounds)
        white_data['score'] += score

        await message.edit(content='分數已更新，白方勝：\n' +
                           '黑方：<@'+str(black_data['user_id'])+'> 完成第 '+str(black_data[battle_type]['total_run'])+' 場比賽\n' +
                           '白方：<@'+str(white_data['user_id'])+'> 完成第 '+str(white_data[battle_type]['total_run'])+' 場比賽\n' +
                           msg + '白方積分增加' + str(score) + ' 分，當前總分為 '+str(white_data['score'])+' 分')

    elif result == 2:  # 平手
        black_data[battle_type]['total_run'] += 1

        if black_data[battle_type]['combo'] < 0:
            black_data[battle_type]['combo'] = 1
        else:
            black_data[battle_type]['combo'] += 1

        if white_data[battle_type]['combo'] < 0:
            white_data[battle_type]['combo'] = 1
        else:
            white_data[battle_type]['combo'] += 1

        score = add_competition_score(
            battle_type, black_data['free']['total_run'], rounds)
        black_data['score'] += score

        white_data[battle_type]['total_run'] += 1
        score = add_competition_score(
            battle_type, white_data['free']['total_run'], rounds)
        white_data['score'] += score

        await message.edit(content='分數已更新，平手：\n' +
                           '黑方：<@'+str(black_data['user_id'])+'> 完成第 '+str(black_data[battle_type]['total_run'])+' 場比賽\n' +
                           '白方：<@'+str(white_data['user_id'])+'> 完成第 '+str(white_data[battle_type]['total_run'])+' 場比賽\n' +
                           msg + '雙方積分增加' + str(score) + ' 分')

    if leaderboard_message == None:
        await try_get_user_leaderboard_message(client, message.guild)
    else:
        await leaderboard_message.edit(content=create_leaderboard_msg())

    return score


def add_competition_record(game_id, battle_type, result, player_data, adversary_data):
    has_record = False

    for record in player_data[battle_type]['history']:
        if record['user_id'] == adversary_data['user_id'] and record['ogs_id'] == adversary_data['ogs_id']:
            if int(game_id) in record['games_id']:
                return -1
            else:
                record['rounds'] += 1
                record['games_id'].append(int(game_id))
                has_record = True
                if result:
                    record['win'] += 1
                return record['rounds']

    if not has_record:
        win = 0
        if result:
            win = 1
        new_history_data = {
            'user_id': adversary_data['user_id'], 'ogs_id': adversary_data['ogs_id'], 'rounds': 1, 'win': win, 'games_id': [int(game_id)]}
        player_data[battle_type]['history'].append(new_history_data)
        return 1


def add_ai_competition_record(battle_type, player_data, adversary_name):
    has_record = False

    for record in player_data[battle_type]['history']:
        if record['user_id'] == adversary_name and record['ogs_id'] == adversary_name:
            record['rounds'] += 1
            record['games_id'].append(0)
            has_record = True
            record['win'] += 1
            return record['rounds']

    if not has_record:
        win = 0
        win = 1
        new_history_data = {
            'user_id': adversary_name, 'ogs_id': adversary_name, 'rounds': 1, 'win': win, 'games_id': [0]}
        player_data[battle_type]['history'].append(new_history_data)
        return 1


def add_app_competition_record(battle_type, result, player_data, adversary_data):
    has_record = False

    for record in player_data[battle_type]['history']:
        if record['user_id'] == adversary_data['user_id'] and record['ogs_id'] == adversary_data['ogs_id']:
            record['rounds'] += 1
            record['games_id'].append(0)
            has_record = True
            if result:
                record['win'] += 1
            return record['rounds']

    if not has_record:
        win = 0
        if result:
            win = 1
        new_history_data = {
            'user_id': adversary_data['user_id'], 'ogs_id': adversary_data['ogs_id'], 'rounds': 1, 'win': win, 'games_id': [0]}
        player_data[battle_type]['history'].append(new_history_data)
        return 1


def add_competition_score(battle_type, total_rounds, adversary_rounds):
    score = 0

    if battle_type == 'free':
        if total_rounds <= 10:
            score = 10
        elif total_rounds > 10 and total_rounds <= 30:
            score = 5
        elif total_rounds > 30:
            score = 2

        if adversary_rounds <= 3:
            score *= 1
        elif adversary_rounds > 3 and adversary_rounds <= 6:
            score *= 0.55
        elif adversary_rounds > 6:
            score *= 0.1
    if battle_type == 'fixed':
        score = 100

    return score


async def register(interaction):
    global competition, register_message

    if str(interaction.user.id) in competition_ban:
        await interaction.response.send_message(f'<@{interaction.user.id}> 你已經被管理員手動禁止了，如果有問題請洽<@{bot_token.owner}>', ephemeral=True)
        return

    if register_message == None:
        await try_get_user_register_message(interaction.client, interaction.guild)

    result = await verify_user_role(interaction.user, 1)

    register_id = discord.utils.get(
        interaction.guild.channels, name=config.register_channel).id

    if result == 'error_no_role':
        await interaction.response.send_message(f'<@{interaction.user.id}> 不符合報名資格 - 沒有身分組 (請先到 <#{register_id}> 註冊身分)', ephemeral=True)
    elif result == 'error_role_incorrect':
        await interaction.response.send_message(f'<@{interaction.user.id}> 不符合報名資格 - 棋力不吻合 (比賽限制的棋力和你的棋力不吻合)', ephemeral=True)
    else:
        user_id = interaction.user.id
        has_data = False
        for competition_data in competition:
            if competition_data['user_id'] == user_id:
                has_data = True
                break

        if not has_data:
            ogs_data = src.ogs.try_find_user_data_by_user(interaction.user)
            if ogs_data == None:
                register_ogs_id = discord.utils.get(
                    interaction.guild.channels, name=config.register_ogs_channel).id
                await interaction.response.send_message(f'找不到對應的OGS帳號資料，請先到 <#{register_ogs_id}> 註冊身分 \nps: **如果已經登錄過帳號** : 請洽 <@{bot_token.owner}> 幫你解決帳號找不到問題', ephemeral=True)
            else:
                raw_data = {'user_id': user_id, 'ogs_id': ogs_data['ogs_id'][0], 'error': 0,
                            'score': 0, 'free': {'total_run': 0, 'combo': 0, 'history': []}, 'fixed': {'total_run': 0, 'combo': 0, 'history': []}, 'event_history': []}
                competition.append(raw_data)
                await interaction.response.send_message('報名成功', ephemeral=True)
                await register_message.edit(content='當前參賽者人數：'+str(len(competition)))
                await trigger_event([('register', raw_data)], interaction.guild)
        else:
            await interaction.response.send_message('重複報名啦!', ephemeral=True)


async def rank(interaction):
    user_id = interaction.user.id
    for competition_data in competition:
        if competition_data['user_id'] == user_id:
            ranking = get_ranking(competition_data['score'])

            free_win_count = 0
            for free_data in competition_data['free']['history']:
                free_win_count += free_data['win']

            fixed_win_count = 0
            for fixed_data in competition_data['fixed']['history']:
                fixed_win_count += fixed_data['win']

            await interaction.response.send_message('名次：第 ' + str(ranking) + ' 名\n當前分數：' +
                                                    str(competition_data['score']) + '\n固定賽：' +
                                                    str(competition_data['fixed']['total_run']) + ' 場 ( '+str(fixed_win_count)+' 勝 '+str(competition_data['fixed']['total_run'] - fixed_win_count)+' 敗 )\n自由賽：' +
                                                    str(competition_data['free']['total_run']) + ' 場 ( '+str(free_win_count)+' 勝 '+str(competition_data['free']['total_run'] - free_win_count)+' 敗 )', ephemeral=True)
            return

    await interaction.response.send_message('沒有報名資料', ephemeral=True)


def get_ranking(score):
    ranking = 1
    for competition_data in competition:
        if competition_data['score'] > score:
            ranking += 1
    return ranking


async def history(interaction):
    user_id = interaction.user.id
    for competition_data in competition:
        if competition_data['user_id'] == user_id:
            msg = ''
            for history_data in competition_data['free']['history']:
                msg += '對手：<@' + str(history_data['user_id']) + '>\n場數：'+str(history_data['rounds'])+'\n戰績：'+str(
                    history_data['win'])+' 勝 '+str(history_data['rounds'] - history_data['win'])+' 敗\n** **\n'
            if len(msg) > 0:
                await interaction.response.send_message(msg, ephemeral=True)
            else:
                await interaction.response.send_message('沒有比賽紀錄', ephemeral=True)
            return

    await interaction.response.send_message('沒有報名資料', ephemeral=True)
    pass


async def try_get_user_register_message(client, guild):
    global register_message

    register_channel = discord.utils.get(
        guild.channels, name=config.competition_register_channel)

    async for message in register_channel.history(limit=200):
        if message.author == client.user:
            if '當前參賽者人數' in message.content:
                register_message = message
    if register_message == None:
        register_message = await register_channel.send('當前參賽者人數 ： '+str(len(competition)))


async def try_get_user_leaderboard_message(client, guild):
    global leaderboard_message

    competition_leaderboard = discord.utils.get(
        guild.channels, name=config.competition_leaderboard_channel)

    async for message in competition_leaderboard.history(limit=200):
        if message.author == client.user:
            leaderboard_message = message
            await leaderboard_message.edit(content=create_leaderboard_msg())

    if leaderboard_message == None:
        leaderboard_message = await competition_leaderboard.send(create_leaderboard_msg())


async def try_get_user_announcement_channel(guild):
    global announcement_channel
    if announcement_channel == None:
        announcement_channel = discord.utils.get(
            guild.channels, name=config.competition_announcement_channel)


def create_leaderboard_msg():
    header = '**當前排名 (前10名)**\n--------------------------\n'
    footer = '\n--------------------------\n*最後更新時間 (' + \
        datetime.datetime.now().astimezone(datetime.timezone(
            datetime.timedelta(hours=8))).strftime("%Y/%m/%d %H:%M") + ')*'
    content = ''

    sort_competition = sorted(
        competition, key=lambda x: x['score'], reverse=True)
    last_rank = 0
    index = 0
    while index < 10:
        if index < len(sort_competition):

            last_rank = get_ranking(sort_competition[index]['score'])

            free_win_count = 0
            for free_data in sort_competition[index]['free']['history']:
                free_win_count += free_data['win']

            fixed_win_count = 0
            for fixed_data in sort_competition[index]['fixed']['history']:
                fixed_win_count += fixed_data['win']

            content += '**第'+rank_table[last_rank]+'名**：<@' + \
                str(sort_competition[index]['user_id']) + \
                '>\n總分：' + str(sort_competition[index]['score'])+'\n固定賽戰績：'+str(fixed_win_count)+'勝'+str(
                    sort_competition[index]['fixed']['total_run']-fixed_win_count)+'敗\n自由賽戰績：' + \
                str(free_win_count)+'勝' + \
                str(sort_competition[index]['free']
                    ['total_run']-free_win_count) + '敗'
        else:
            last_rank += 1
            content += '**第'+rank_table[last_rank]+'名**：從缺'
        if index < 9:
            content += '\n** **\n'
        index += 1

    return header + content + footer


async def create_outcome_msg(reply_msg, result_type, ways_to_win, black_player, white_player):
    msg = '比賽結果：'

    black_data = try_find_user_data_by_ogs(black_player)
    white_data = try_find_user_data_by_ogs(white_player)

    if black_data == None:
        await reply_msg.edit(content=f'檢查成績失敗，找不到黑方的比賽資料\nps: **如果已經登記過帳號** : 請洽 <@{bot_token.owner}> 幫你解決帳號找不到問題')
        return False

    if white_data == None:
        await reply_msg.edit(content=f'檢查成績失敗，找不到白方的比賽資料\nps: **如果已經登記過帳號** : 請洽 <@{bot_token.owner}> 幫你解決帳號找不到問題')
        return False

    if result_type == 0:
        msg += '<@'+str(black_data['user_id'])+'>勝'
    elif result_type == 1:
        msg += '<@'+str(white_data['user_id'])+'>勝'
    elif result_type == 2:
        msg += '平局'

    if ways_to_win == '投降':
        msg += '於 對手投降'
    elif ways_to_win == '超時':
        msg += '於 對手超時'
    else:
        msg += ' ' + ways_to_win + ' 目'
    msg += '，正在更新分數...'
    await reply_msg.edit(content=msg)
    return True


async def verify_user_role(autohr, level):

    d_role = discord.utils.get(autohr.guild.roles, name=config.d_id)
    k1_role = discord.utils.get(autohr.guild.roles, name=config.k1_id)
    k3_role = discord.utils.get(autohr.guild.roles, name=config.k3_id)
    k5_role = discord.utils.get(autohr.guild.roles, name=config.k5_id)
    k7_role = discord.utils.get(autohr.guild.roles, name=config.k7_id)
    k10_role = discord.utils.get(autohr.guild.roles, name=config.k10_id)
    k15_role = discord.utils.get(autohr.guild.roles, name=config.k15_id)
    k20_role = discord.utils.get(autohr.guild.roles, name=config.k20_id)
    k25_role = discord.utils.get(autohr.guild.roles, name=config.k25_id)
    k30_role = discord.utils.get(autohr.guild.roles, name=config.k30_id)

    if ((d_role not in autohr.roles) and
        (k1_role not in autohr.roles) and
        (k3_role not in autohr.roles) and
        (k5_role not in autohr.roles) and
        (k7_role not in autohr.roles) and
        (k10_role not in autohr.roles) and
        (k15_role not in autohr.roles) and
        (k20_role not in autohr.roles) and
        (k25_role not in autohr.roles) and
            (k30_role not in autohr.roles)):
        return 'error_no_role'
    else:
        if level == 1:
            if (d_role in autohr.roles or
                    k1_role in autohr.roles or
                    k3_role in autohr.roles or
                    k5_role in autohr.roles or
                    k7_role in autohr.roles):
                return 'error_role_incorrect'
            else:
                return 'valid'
        elif level == 2:
            if (d_role in autohr.roles or
                    k1_role in autohr.roles or
                    k3_role in autohr.roles or
                    k10_role in autohr.roles or
                    k15_role in autohr.roles or
                    k20_role in autohr.roles or
                    k25_role in autohr.roles or
                    k30_role in autohr.roles):
                return 'error_role_incorrect'
            else:
                return 'valid'
        elif level == 3:
            if (k5_role in autohr.roles or
                    k7_role in autohr.roles or
                    k10_role in autohr.roles or
                    k15_role in autohr.roles or
                    k20_role in autohr.roles or
                    k25_role in autohr.roles or
                    k30_role in autohr.roles):
                return 'error_role_incorrect'
            else:
                return 'valid'
        else:
            return 'valid'


def event_phaser(result_type, ways_to_win, moves, black_player, white_player, bang_win, bang_loss, score):

    trigger_event = []

    user_win_data = None
    user_loss_data = None

    if result_type == 0:
        user_win_data = try_find_user_data_by_ogs(black_player)
        user_loss_data = try_find_user_data_by_ogs(white_player)

    if result_type == 1:
        user_win_data = try_find_user_data_by_ogs(white_player)
        user_loss_data = try_find_user_data_by_ogs(black_player)

    if ('first_blood' not in user_win_data['event_history']) and (user_win_data['score'] - score == 0):
        user_win_data['event_history'].append('first_blood')
        trigger_event.append(('first_blood', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    win_count = 0
    for history_data in user_win_data['free']['history']:
        win_count += history_data['win']

    if 'win_15' not in user_win_data['event_history']:
        if win_count >= 15:
            user_win_data['event_history'].append('win_15')
            trigger_event.append(('win_15', user_win_data))

    if 'win_10' not in user_win_data['event_history']:
        if win_count >= 10:
            user_win_data['event_history'].append('win_10')
            trigger_event.append(('win_10', user_win_data))

    if 'win_5' not in user_win_data['event_history']:
        if win_count >= 5:
            user_win_data['event_history'].append('win_5')
            trigger_event.append(('win_5', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if 'round_30' not in user_win_data['event_history'] and user_win_data['free']['total_run'] == 30:
        user_win_data['event_history'].append('round_30')
        trigger_event.append(('round_30', user_win_data))

    if 'round_30' not in user_loss_data['event_history'] and user_loss_data['free']['total_run'] == 30:
        user_loss_data['event_history'].append('round_30')
        trigger_event.append(('round_30', user_loss_data))

    elif 'combo_win_10' not in user_win_data['event_history'] and user_win_data['free']['combo'] >= 10:
        user_win_data['event_history'].append('combo_win_10')
        trigger_event.append(('combo_win_10', user_win_data))

    elif 'combo_loss_10' not in user_loss_data['event_history'] and user_loss_data['free']['combo'] <= -10:
        user_loss_data['event_history'].append('combo_loss_10')
        trigger_event.append(('combo_loss_10', user_loss_data))

    elif 'combo_win_5' not in user_win_data['event_history'] and user_win_data['free']['combo'] >= 5:
        user_win_data['event_history'].append('combo_win_5')
        trigger_event.append(('combo_win_5', user_win_data))

    elif 'combo_loss_5' not in user_loss_data['event_history'] and user_loss_data['free']['combo'] <= -5:
        user_loss_data['event_history'].append('combo_loss_5')
        trigger_event.append(('combo_loss_5', user_loss_data))

    if 'combo_win_3' not in user_win_data['event_history'] and user_win_data['free']['combo'] >= 3:
        user_win_data['event_history'].append('combo_win_3')
        trigger_event.append(('combo_win_3', user_win_data))

    if 'combo_loss_3' not in user_loss_data['event_history'] and user_loss_data['free']['combo'] <= -3:
        user_loss_data['event_history'].append('combo_loss_3')
        trigger_event.append(('combo_loss_3', user_loss_data))

    if len(trigger_event) > 0:
        return trigger_event

    if len(competition) >= 2:
        if get_ranking(user_win_data['score']) == 1:
            sort_competition = sorted(
                competition, key=lambda x: x['score'], reverse=True)
            if user_win_data['user_id'] == sort_competition[0]['user_id']:
                if user_win_data['score'] - sort_competition[1]['score'] >= 200:
                    if 'hightest' not in user_win_data['event_history']:
                        user_win_data['event_history'].append('hightest')
                        trigger_event.append(('hightest', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if 'bang_win' not in user_win_data['event_history'] and bang_win:
        user_win_data['event_history'].append('bang_win')
        trigger_event.append(('bang_win', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if 'bang_loss' not in user_loss_data['event_history'] and bang_loss:
        user_win_data['event_history'].append('bang_loss')
        trigger_event.append(('bang_loss', user_loss_data))

    if len(trigger_event) > 0:
        return trigger_event

    if 'too_many_rounds_3' not in user_win_data['event_history']:
        for history_data in user_win_data['free']['history']:
            if history_data['user_id'] == user_loss_data['user_id']:
                if history_data['rounds'] >= 3:
                    user_win_data['event_history'].append('too_many_rounds_3')
                    trigger_event.append(('too_many_rounds_3', user_win_data))

    if 'too_many_rounds_6' not in user_win_data['event_history']:
        for history_data in user_win_data['free']['history']:
            if history_data['user_id'] == user_loss_data['user_id']:
                if history_data['rounds'] >= 6:
                    user_win_data['event_history'].append('too_many_rounds_6')
                    trigger_event.append(('too_many_rounds_6', user_loss_data))

    if len(trigger_event) > 0:
        return trigger_event

    if get_ranking(user_win_data['score']) == 1:
        if get_ranking(user_win_data['score'] - score) > 2:
            trigger_event.append(('winner_candidate', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if 'win_time' not in user_win_data['event_history'] and ways_to_win == '超時':
        user_win_data['event_history'].append('win_time')
        trigger_event.append(('win_time', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    win_territory = 0
    if not ways_to_win == '投降':
        win_territory = float(ways_to_win)

    if 'territory_100' not in user_win_data['event_history'] and win_territory > 100:
        user_win_data['event_history'].append('territory_100')
        trigger_event.append(('territory_100', user_win_data))

    if 'moves_200' not in user_win_data['event_history'] and moves >= 200:
        user_win_data['event_history'].append('moves_200')
        trigger_event.append(('moves_200', user_win_data))

    if 'moves_100' not in user_win_data['event_history'] and moves <= 100:
        user_win_data['event_history'].append('moves_100')
        trigger_event.append(('moves_100', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if len(trigger_event) == 0:
        if random.randint(1, 4) == 4:
            trigger_event.append(('lucky', user_win_data))

    return trigger_event


def event_ai_phaser(player_id, score):

    trigger_event = []

    user_win_data = None

    user_win_data = try_find_user_data_by_id(player_id)

    if ('first_blood' not in user_win_data['event_history']) and (user_win_data['score'] - score == 0):
        user_win_data['event_history'].append('first_blood')
        trigger_event.append(('first_blood', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    win_count = 0
    for history_data in user_win_data['free']['history']:
        win_count += history_data['win']

    if 'win_15' not in user_win_data['event_history']:
        if win_count >= 15:
            user_win_data['event_history'].append('win_15')
            trigger_event.append(('win_15', user_win_data))

    if 'win_10' not in user_win_data['event_history']:
        if win_count >= 10:
            user_win_data['event_history'].append('win_10')
            trigger_event.append(('win_10', user_win_data))

    if 'win_5' not in user_win_data['event_history']:
        if win_count >= 5:
            user_win_data['event_history'].append('win_5')
            trigger_event.append(('win_5', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if 'round_30' not in user_win_data['event_history'] and user_win_data['free']['total_run'] == 30:
        user_win_data['event_history'].append('round_30')
        trigger_event.append(('round_30', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if len(competition) >= 2:
        if get_ranking(user_win_data['score']) == 1:
            sort_competition = sorted(
                competition, key=lambda x: x['score'], reverse=True)
            if user_win_data['user_id'] == sort_competition[0]['user_id']:
                if user_win_data['score'] - sort_competition[1]['score'] >= 200:
                    if 'hightest' not in user_win_data['event_history']:
                        user_win_data['event_history'].append('hightest')
                        trigger_event.append(('hightest', user_win_data))

    if len(trigger_event) > 0:
        return trigger_event

    if get_ranking(user_win_data['score']) == 1:
        if get_ranking(user_win_data['score'] - score) > 2:
            trigger_event.append(('winner_candidate', user_win_data))

    return trigger_event


async def trigger_event(trigger_events, guild):
    # 'error_too_many' = 登記成績錯誤太多次
    # 'register' = 註冊成功
    # 'winner_candidate' = 變成第一名
    # 'combo_win_10' = 連勝10場
    # 'combo_win_5' = 連勝5場
    # 'combo_win_3' = 連勝3場
    # 'combo_loss_10' = 連敗10場
    # 'combo_loss_5' = 連敗5場
    # 'combo_loss_3' = 連敗3場
    # 'hightest' = 領先第二名200分
    # 'bang_win' = 連敗3場以上逆轉勝
    # 'bang_loss' = 連勝3場以上滑鐵盧
    # 'round_30' = 累積30場比賽
    # 'too_many_rounds_6' = 和同一個對手連戰6場，輸家視角
    # 'too_many_rounds_3' = 和同一個對手連戰3場，贏家視角
    # 'first_blood' = 首勝
    # 'win_15' = 累積15勝
    # 'win_10' = 累積10勝
    # 'win_5' = 累積5勝
    # 'win_time' = 對手超時負
    # 'territory_100' = 贏對手超過100目
    # 'moves_200' = 兩百手後才獲勝
    # 'moves_100' = 一百手內獲勝
    # 'lucky' = 運氣抽到
    global announcement_channel
    if announcement_channel == None:
        await try_get_user_announcement_channel(guild)

    for trigger_event in trigger_events:
        for announcement_data in competition_announcement:
            if announcement_data['key'] == trigger_event[0]:
                msg = announcement_data['value'][random.randint(
                    0, len(announcement_data['value'])-1)]
                msg = functions.util.str_replace(
                    msg, 'USERID', str(trigger_event[1]['user_id']))
                await announcement_channel.send(msg)


def save_json(path, ban_path):
    f = open(path, 'w')
    json.dump(competition, f, indent=0)
    f = open(ban_path, 'w')
    json.dump(competition_ban, f, indent=0)

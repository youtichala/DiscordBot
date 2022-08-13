import platform

root_path = ''
entrance_channel = '玄關'
register_channel = '身分簽到處'
competition_announcement_channel = '公告'
competition_leaderboard_channel = '排行榜'
competition_register_channel = '控制板'
competition_record_channel = '成績登錄區'
register_ogs_channel = 'ogs群登記處'
user_level_path = 'data/user_level.json'
competition_path = 'data/competition.json'
competition_ban_path = 'data/competition_ban.json'
competition_announcement_path = 'data/competition_announcement.json'
ogs_path = 'data/ogs.json'
chat_path = 'data/chat.json'
story_path = 'data/story.json'
prefix = '黑小嘉'
score_prefix = '積分賽'
d_id = '段位大佬'
k1_id = '1K'
k3_id = '3K'
k5_id = '5K'
k7_id = '7K'
k10_id = '10K'
k15_id = '15K'
k20_id = '20K'
k25_id = '25K'
k30_id = '30K'
d_emoji = '<:numberd:994881414686318612>'
k1_emoji = '<:number1:994881416598929470>'
k3_emoji = '<:number3:994881418796736572>'
k5_emoji = '<:number5:995258632193183794>'
k7_emoji = '<:number7:994881420092784691>'
k10_emoji = '<:number10:994881280086908968>'
k15_emoji = '<:number15:994881281785602108>'
k20_emoji = '<:number20:994881283723374632>'
k25_emoji = '<:number25:994881285724049498>'
k30_emoji = '<:number30:994881544655212593>'
cool_down_time = 60

platform_str = platform.system()


def setup_path():
    global root_path
    if platform_str == 'Windows':
        root_path = 'D:/Project/Python/DiscordGoBot/'
    elif platform_str == 'Darwin':
        root_path = '/Users/microogle/DiscordGoBot/'
    elif platform_str == 'Linux':
        root_path = '/home/user_name/DiscordGoBot/'
    else:
        root_path = 'not_support_path'


def get_root_path():
    if root_path == '':
        setup_path()

    return root_path

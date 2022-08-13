import requests
import re
import json
from time import time

access_token = None
refresh_token = None
start = None
end = None


def setup():
    global end
    end = time()
    if access_token == None:
        get_access_token()
    elif end - start >= 36000:
        refresh_access_token()


# 取得Token
def get_access_token():
    global access_token, refresh_token
    global start
    r = requests.post('https://online-go.com/oauth2/token/',
                      data={"username": "USERNAME",
                            "password": "PASSWORD",
                            "client_id": "CLIENT_ID",
                            "grant_type": "password"})

    access_token = r.json()['access_token']
    refresh_token = r.json()['refresh_token']
    start = time()


# 取得Token
def refresh_access_token():
    global access_token, refresh_token

    url = 'https://online-go.com/oauth2/token/'
    data = {'refresh_token': refresh_token,
            'client_id': 'CLIENT_ID',
            'grant_type': 'refresh_token'}

    r = requests.post(url=url, data=data)
    access_token = r.json()['access_token']
    refresh_token = r.json()['refresh_token']


# 取得社團成員
# [{
#    "id":186170,
#    "user":{
#       "id":1159851,
#       "username":"aaa2188",
#       "country":"tw",
#       "icon":"https://b0c2ddc39d13e1c0ddad-93a52a5bc9e7cc06050c1a999beb3694.ssl.cf1.rackcdn.com/a10d52888ca8d5e11528eeeeb249f017-32.png",
#       "ratings":{
#          "version":5,
#          "overall":{
#             "rating":1500,
#             "deviation":350,
#             "volatility":0.06
#          }
#       },
#       "ranking":24.303382182144386,
#       "professional":false,
#       "ui_class":"provisional"
#    },
#    "is_primary":false,
#    "is_admin":false
# },.....]


def get_group_menber():
    setup()
    menber = []
    url = 'http://online-go.com/api/v1/groups/11838/members/'
    headers = {'Authorization': f"Bearer {access_token}"}

    resp = requests.get(url, headers=headers)

    while resp.json()['next'] != None:
        for user in resp.json()['results']:
            menber.append(user)
        url = resp.json()['next']
        resp = requests.get(url, headers=headers)

    for user in resp.json()['results']:
        menber.append(user)

    return menber


# 取得玩家資訊
def get_gamer_data(id):
    setup()
    url = f'https://online-go.com/api/v1/players/{id}'
    headers = {'Authorization': f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    return resp.json()


# 創建比賽
def creat_tournaments(name, description, start_time):
    setup()
    url = 'https://online-go.com/api/v1/tournaments/'
    headers = {'Authorization': f"Bearer {access_token}"}
    game = {
        "id": 90926,
        "name": name,
        "description": description,
        "schedule": None,
        "title": None,
        "tournament_type": "elimination",
        "handicap": 0,
        "rules": "japanese",
        "time_control_parameters": {
            "system": "byoyomi",
            "time_control": "byoyomi",
            "speed": "live",
            "pause_on_weekends": False,
            "main_time": 600,
            "period_time": 30,
            "periods": 3
        },
        "is_open": True,
        "exclude_provisional": False,
        "group": 11838,
        "player_is_member_of_group": True,
        "auto_start_on_max": True,
        "time_start": start_time,  # "2022-06-10T09:00:00-04:00",
        "players_start": 2,
        "first_pairing_method": "slide",
        "subsequent_pairing_method": "strength",
        "min_ranking": 5,
        "max_ranking": 38,
        "analysis_enabled": True,
        "exclusivity": "invite",
        "started": None,
        "ended": None,
        "start_waiting": None,
        "board_size": 19,
        "active_round": None,
        "settings": {
            "maximum_players": 2,
            "active_round": None
        },
        "rounds": None,
        "icon": "https://b0c2ddc39d13e1c0ddad-93a52a5bc9e7cc06050c1a999beb3694.ssl.cf1.rackcdn.com/ff32df4d306f63a57b04de2d403a9d5b-15.png",
        "scheduled_rounds": False,
        "can_administer": True,
        "opengotha_standings": None
    }
    resp = requests.post(url, headers=headers, json=game)
    print(resp.text)
    if 'success' in resp.json():
        return resp.json()['id']
    else:
        return None


# 邀請比賽
def invite_menber_to_tournaments(user_name, room_id):
    setup()
    url = f'https://online-go.com/api/v1/tournaments/{room_id}/players'
    headers = {'Authorization': f"Bearer {access_token}"}
    game = {"username": user_name}
    resp = requests.post(url, headers=headers, json=game)
    print(resp.json())
    if 'success' in resp.json():
        return resp.json()['success']
    else:
        return resp.json()['error']


# 開始比賽
def get_start_menber(id):
    setup()
    url = f'https://online-go.com/api/v1/tournaments/{id}/start'
    headers = {'Authorization': f"Bearer {access_token}"}
    resp = requests.post(url, headers=headers)
    if 'success' in resp.json():
        return True
    return False


# 取得opengotha_data
def get_opengotha_data(id):
    setup()
    url = f'https://online-go.com/api/v1/tournaments/{id}/opengotha'
    headers = {'Authorization': f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    print(resp.json())
# print(creat_tournaments('name', 'description','2022-06-10T09:00:00-04:00'))


# 取得比賽
def get_games_data(id):
    setup()
    url = f'https://online-go.com/api/v1/games/{id}'
    headers = {'Authorization': f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    else:
        return resp.json()


# 刪除比賽
# setup()
# url = 'https://online-go.com/api/v1/tournaments/90505'
# headers = {'Authorization': f"Bearer {access_token}"}
# resp = requests.delete(url, headers=headers)
# print(resp.text)


# 刪除比賽紀錄
# setup()
# url = 'https://online-go.com/api/v1/tournament_records/1167'
# headers = {'Authorization': f"Bearer {access_token}"}
# resp = requests.delete(url, headers=headers)
# print(resp.text)


# 取得邀請
# setup()
# url = 'https://online-go.com/api/v1/me/tournaments/invitations'
# headers = {'Authorization': f"Bearer {access_token}"}
# resp = requests.get(url, headers=headers)
# print(resp.text)


# 接受邀請
# setup()
# url = 'https://online-go.com/api/v1/me/tournaments/invitations'
# headers = {'Authorization': f"Bearer {access_token}"}
# game = {"request_id": 86371}
# resp = requests.post(url, headers=headers, json = game)
# print(resp.text)


# 拒絕邀請
# url = 'https://online-go.com/api/v1/me/tournaments/invitations'
# headers = {'Authorization': f"Bearer {access_token}"}
# game = {"delete": True, "request_id": 86371}
# print(resp.text)
# print(resp.text)


# region 測試中功能
session_requests = None


def login():  # 太頻繁呼叫會被禁止喔
    global session_requests
    session_requests = requests.session()
    result = session_requests.get("https://www.101weiqi.com/login/")
    authenticity_token = re.search(
        "'csrfmiddlewaretoken\' value=(.*) />", result.text).group()
    authenticity_token = authenticity_token.replace(
        "'csrfmiddlewaretoken' value='", "")
    authenticity_token = authenticity_token.replace("' />", "")

    headers = {
        'authority': 'www.101weiqi.com',
        'method': 'POST',
        'path': '/loginreq/',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        'content-length': '138',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'csrftoken='+authenticity_token+'',
        'origin': 'https://www.101weiqi.com',
        'referer': 'https://www.101weiqi.com/login/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36',
    }

    payload = {
        'form_username': 'form_username',
        'form_password': 'form_password',
        'csrfmiddlewaretoken': authenticity_token
    }

    result = session_requests.post(
        'https://www.101weiqi.com/loginreq/', data=payload, headers=headers)
    print(result)
    print(result.text)


def get_question(level, id):
    global session_requests
    if session_requests == None:
        login()

    url = f'https://www.101weiqi.com/{level}/{id}/'
    resp = session_requests.get(url)
    if resp.status_code != 200:
        print(resp)
        return None, None, None, None, None, None
    else:
        if re.search("var g_qq = (.*);var taskinfo", resp.text) != None:
            result = re.search(
                "var g_qq = (.*);var taskinfo", resp.text).group()
            result = result.replace("var g_qq = ", "")
            result = result.replace(";var taskinfo", "")
            jsonValue = json.loads(result)
            questions = jsonValue['prepos']
            size = jsonValue['lu']
            pts = None
            answer_name = jsonValue['username']
            for answer_data in jsonValue['answers']:
                if answer_data['username'] == answer_name:
                    pts = answer_data['pts']

            return questions, pts, size, jsonValue['pos_x1'], jsonValue['pos_x2']
        else:
            session_requests = None
            print(resp.text)
            return None, None, None, None, None, None


def get_question_test(level, id):
    resp_text = "var g_qq = {\"status\": 2, \"pos_y1\": 0, \"pos_y2\": 6, \"islei\": false, \"myoper\": {\"mystar\": false, \"tags\": [], \"mytags\": []}, \"layoutnumber\": 1, \"qshids\": [], \"userlevel\": 105, \"orgid\": 0, \"vv\": 9, \"signs\": [], \"vote\": 5.0, \"bookinfos\": [], \"qtype\": 1, \"id\": 295223, \"fine_status\": 3, \"points\": [], \"publicid\": 260670, \"title\": \"\", \"ineb\": false, \"comments\": [], \"specs\": [], \"lu\": 19, \"max_levelname\": \"\", \"hasspec\": false, \"blackfirst\": true, \"luozis\": [], \"username\": \"kenny\", \"pos_x2\": 18, \"pos_x1\": 12, \"andata\": {\"0\": {\"c\": 0, \"subs\": [1, 3, 5], \"pt\": \"\", \"f\": 0, \"tip\": \"\", \"o\": 0, \"p\": 0, \"u\": 0, \"aids\": [], \"id\": 0}, \"1\": {\"c\": 0, \"subs\": [2], \"pt\": \"qa\", \"f\": 1, \"tip\": \"\", \"o\": 0, \"p\": 0, \"u\": 0, \"aids\": [1851064], \"id\": 1}, \"2\": {\"c\": 0, \"subs\": [], \"pt\": \"sb\", \"f\": 1, \"tip\": \"\", \"o\": 0, \"p\": 1, \"u\": 0, \"aids\": [1851064], \"id\": 2}, \"3\": {\"c\": 0, \"subs\": [4], \"pt\": \"rc\", \"f\": 1, \"tip\": \"\", \"o\": 0, \"p\": 0, \"u\": 0, \"aids\": [1851063], \"id\": 3}, \"4\": {\"c\": 0, \"subs\": [], \"pt\": \"sb\", \"f\": 1, \"tip\": \"\", \"o\": 0, \"p\": 3, \"u\": 0, \"aids\": [1851063], \"id\": 4}, \"5\": {\"c\": 0, \"subs\": [], \"pt\": \"sb\", \"f\": 0, \"tip\": \"\", \"o\": 1, \"p\": 0, \"u\": 0, \"aids\": [1851062], \"id\": 5}}, \"edit_count\": 0, \"answers\": [{\"username\": \"kenny\", \"change_count\": 0, \"ty\": 3, \"nu\": 3, \"userid\": 23199, \"st\": 2, \"ok_count\": 0, \"error_count\": 0, \"bad_count\": 50, \"v\": 0, \"pts\": [{\"p\": \"qa\", \"c\": \"\"}, {\"p\": \"sb\", \"c\": \"\"}], \"id\": 1851064}, {\"username\": \"kenny\", \"change_count\": 0, \"ty\": 3, \"nu\": 2, \"userid\": 23199, \"st\": 2, \"ok_count\": 0, \"error_count\": 0, \"bad_count\": 50, \"v\": 0, \"pts\": [{\"p\": \"rc\", \"c\": \"\"}, {\"p\": \"sb\", \"c\": \"\"}], \"id\": 1851063}, {\"username\": \"kenny\", \"change_count\": 0, \"ty\": 1, \"nu\": 1, \"userid\": 23199, \"st\": 2, \"ok_count\": 50, \"error_count\": 0, \"bad_count\": 0, \"v\": 0, \"pts\": [{\"p\": \"sb\", \"c\": \"\"}], \"id\": 1851062}], \"is_share\": true, \"min_levelname\": \"\", \"taskresult\": {\"ok_nums\": [2, 6, 32, 85, 183, 141, 164, 110, 36, 18, 17, 11, 9, 5, 6, 0, 2, 2, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], \"ok_total\": 832, \"fail_nums\": [0, 2, 9, 6, 11, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], \"fail_total\": 34}, \"qtypename\": \"\u6b7b\u6d3b\u9898\", \"hasbook\": false, \"issingle\": true, \"xuandians\": [], \"sms_count\": 3, \"nexterrorurl\": \"\", \"sy\": 7, \"enable_answer\": true, \"name\": \"\", \"attr_type\": 0, \"ans_count\": 3, \"userid\": 23199, \"taotaiid\": 0, \"is_public\": true, \"sx\": 7, \"disuse\": 0, \"isguess\": false, \"prepos\": [[\"pa\", \"pb\", \"pc\", \"qc\", \"qd\", \"ra\", \"rd\", \"sc\"], [\"oa\", \"ob\", \"oc\", \"od\", \"pd\", \"qb\", \"qe\", \"rb\", \"re\", \"sd\", \"se\"]], \"myan\": null, \"options\": [], \"levelname\": \"10K\"};var taskinfo "
    resp_text = "var g_qq = {\"status\": 2,\"pos_y1\": 0,\"pos_y2\": 7,\"islei\": false,\"myoper\": {\"mystar\": false,\"tags\": [],\"mytags\": []},\"layoutnumber\": 1,\"qshids\": [],\"userlevel\": 105,\"orgid\": 0,\"vv\": 6,\"signs\": [],\"vote\": 4.4,\"bookinfos\": [{\"pinyin\": \"lichanhaoshoujin\",\"bookname\": \"\u674e\u660c\u9550\u7cbe\u8bb2\u56f4\u68cb\u624b\u7b4b\u5168\u96c6\",\"nodename\": \"1\",\"bookid\": 321,\"bookurl\": \"lichanhaoshoujin\"}],\"qtype\": 21,\"id\": 2,\"fine_status\": 3,\"points\": [],\"publicid\": 2,\"title\": \"\",\"ineb\": false,\"specs\": [],\"lu\": 19,\"max_levelname\": \"7K\",\"hasspec\": false,\"blackfirst\": true,\"luozis\": [],\"username\": \"admin\",\"pos_x2\": 18,\"pos_x1\": 11,\"andata\": {\"0\": {\"c\": 0,\"subs\": [1,6,9,13,15],\"pt\": \"\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [],\"id\": 0},\"1\": {\"c\": 1,\"subs\": [2,21],\"pt\": \"pb\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 0,\"u\": 0,\"aids\": [433948,70894,325588,1066160],\"id\": 1},\"2\": {\"c\": 1,\"subs\": [3],\"pt\": \"pa\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 1,\"u\": 0,\"aids\": [433948,70894,325588],\"id\": 2},\"3\": {\"c\": 1,\"subs\": [4,19],\"pt\": \"na\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 2,\"u\": 0,\"aids\": [433948,70894,325588],\"id\": 3},\"4\": {\"c\": 1,\"subs\": [5],\"pt\": \"sa\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 3,\"u\": 0,\"aids\": [433948],\"id\": 4},\"5\": {\"c\": 1,\"subs\": [],\"pt\": \"pb\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 4,\"u\": 0,\"aids\": [433948],\"id\": 5},\"6\": {\"c\": 1,\"subs\": [7,23],\"pt\": \"pa\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 0,\"u\": 0,\"aids\": [70893,325589,443917,604428],\"id\": 6},\"7\": {\"c\": 1,\"subs\": [8],\"pt\": \"pb\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 6,\"u\": 0,\"aids\": [70893,325589,443917],\"id\": 7},\"8\": {\"c\": 1,\"subs\": [11,17],\"pt\": \"na\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 7,\"u\": 0,\"aids\": [70893,325589,443917],\"id\": 8},\"9\": {\"c\": 0,\"subs\": [10],\"pt\": \"na\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [287706],\"id\": 9},\"10\": {\"c\": 0,\"subs\": [],\"pt\": \"sb\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 9,\"u\": 0,\"aids\": [287706],\"id\": 10},\"11\": {\"c\": 0,\"subs\": [12],\"pt\": \"sb\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 8,\"u\": 0,\"aids\": [325589],\"id\": 11},\"12\": {\"c\": 0,\"subs\": [],\"pt\": \"pa\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 11,\"u\": 0,\"aids\": [325589],\"id\": 12},\"13\": {\"c\": 0,\"subs\": [14],\"pt\": \"sd\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [604429],\"id\": 13},\"14\": {\"c\": 0,\"subs\": [],\"pt\": \"sb\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 13,\"u\": 0,\"aids\": [604429],\"id\": 14},\"15\": {\"c\": 0,\"subs\": [16],\"pt\": \"sb\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [270094],\"id\": 15},\"16\": {\"c\": 0,\"subs\": [],\"pt\": \"sa\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 15,\"u\": 0,\"aids\": [270094],\"id\": 16},\"17\": {\"c\": 1,\"subs\": [18],\"pt\": \"sa\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 8,\"u\": 0,\"aids\": [443917],\"id\": 17},\"18\": {\"c\": 1,\"subs\": [],\"pt\": \"pa\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 17,\"u\": 0,\"aids\": [443917],\"id\": 18},\"19\": {\"c\": 0,\"subs\": [20],\"pt\": \"sb\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 3,\"u\": 0,\"aids\": [325588],\"id\": 19},\"20\": {\"c\": 0,\"subs\": [],\"pt\": \"pb\",\"f\": 0,\"tip\": \"\",\"o\": 1,\"p\": 19,\"u\": 0,\"aids\": [325588],\"id\": 20},\"21\": {\"c\": 1,\"subs\": [22],\"pt\": \"sb\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 1,\"u\": 0,\"aids\": [1066160],\"id\": 21},\"22\": {\"c\": 1,\"subs\": [],\"pt\": \"pa\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 21,\"u\": 0,\"aids\": [1066160],\"id\": 22},\"23\": {\"c\": 1,\"subs\": [24],\"pt\": \"sb\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 6,\"u\": 0,\"aids\": [604428],\"id\": 23},\"24\": {\"c\": 1,\"subs\": [],\"pt\": \"pb\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 23,\"u\": 0,\"aids\": [604428],\"id\": 24}},\"edit_count\": 1,\"answers\": [{\"username\": \"wx_463632111726\",\"change_count\": 11,\"ty\": 2,\"nu\": 11,\"userid\": 26555,\"st\": 2,\"ok_count\": 3,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pb\",\"c\": \" \"},{\"p\": \"pa\",\"c\": \" \"},{\"p\": \"na\",\"c\": \" \"},{\"p\": \"sa\",\"c\": \" \"},{\"p\": \"pb\",\"c\": \" \"}],\"id\": 433948},{\"username\": \"roboter\",\"change_count\": 1,\"ty\": 1,\"nu\": 1,\"userid\": 2,\"st\": 2,\"ok_count\": 12,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pa\",\"c\": \"\"},{\"p\": \"pb\",\"c\": \"\"},{\"p\": \"na\",\"c\": \"\"}],\"id\": 70893},{\"username\": \"roboter\",\"change_count\": 0,\"ty\": 1,\"nu\": 2,\"userid\": 2,\"st\": 2,\"ok_count\": 16,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pb\",\"c\": \"\"},{\"p\": \"pa\",\"c\": \"\"},{\"p\": \"na\",\"c\": \"\"}],\"id\": 70894},{\"username\": \"kenny\",\"change_count\": 0,\"ty\": 3,\"nu\": 6,\"userid\": 23199,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 10,\"v\": 0,\"pts\": [{\"p\": \"na\",\"c\": \" \"},{\"p\": \"sb\",\"c\": \" \"}],\"id\": 287706},{\"username\": \"\u5c71\u5d50\u9727\u6c34\",\"change_count\": 0,\"ty\": 1,\"nu\": 8,\"userid\": 18636,\"st\": 2,\"ok_count\": 12,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pa\",\"c\": \" \"},{\"p\": \"pb\",\"c\": \" \"},{\"p\": \"na\",\"c\": \" \"},{\"p\": \"sb\",\"c\": \" \"},{\"p\": \"pa\",\"c\": \" \"}],\"id\": 325589},{\"username\": \"QQde\u5bc6\u7801\",\"change_count\": 0,\"ty\": 3,\"nu\": 16,\"userid\": 4323,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 10,\"v\": 0,\"pts\": [{\"p\": \"sd\",\"c\": \"\"},{\"p\": \"sb\",\"c\": \"\"}],\"id\": 604429},{\"username\": \"haoz\",\"change_count\": 0,\"ty\": 3,\"nu\": 5,\"userid\": 14560,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 12,\"v\": 0,\"pts\": [{\"p\": \"sb\",\"c\": \" \"},{\"p\": \"sa\",\"c\": \" \"}],\"id\": 270094},{\"username\": \"AKJ(T-T)\",\"change_count\": 11,\"ty\": 2,\"nu\": 12,\"userid\": 50236,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pa\",\"c\": \" \"},{\"p\": \"pb\",\"c\": \" \"},{\"p\": \"na\",\"c\": \" \"},{\"p\": \"sa\",\"c\": \" \"},{\"p\": \"pa\",\"c\": \" \"}],\"id\": 443917},{\"username\": \"\u5c71\u5d50\u9727\u6c34\",\"change_count\": 0,\"ty\": 1,\"nu\": 7,\"userid\": 18636,\"st\": 2,\"ok_count\": 19,\"error_count\": 0,\"bad_count\": 1,\"v\": 0,\"pts\": [{\"p\": \"pb\",\"c\": \" \"},{\"p\": \"pa\",\"c\": \" \"},{\"p\": \"na\",\"c\": \" \"},{\"p\": \"sb\",\"c\": \" \"},{\"p\": \"pb\",\"c\": \" \"}],\"id\": 325588},{\"username\": \"\u6c6a\u65b0\u8d8a\",\"change_count\": 51,\"ty\": 2,\"nu\": 19,\"userid\": 485873,\"st\": 2,\"ok_count\": 1,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pb\",\"c\": \"\"},{\"p\": \"sb\",\"c\": \"\"},{\"p\": \"pa\",\"c\": \"\"}],\"id\": 1066160},{\"username\": \"QQde\u5bc6\u7801\",\"change_count\": 12,\"ty\": 2,\"nu\": 15,\"userid\": 4323,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"pa\",\"c\": \"\"},{\"p\": \"sb\",\"c\": \"\"},{\"p\": \"pb\",\"c\": \"\"}],\"id\": 604428}],\"is_share\": true,\"min_levelname\": \"11K\",\"taskresult\": {\"ok_nums\": [1358,1324,1814,2124,2413,2422,2042,1637,1247,894,742,591,462,381,305,237,166,163,166,115,79,60,54,50,34,56,72,10,11,23],\"ok_total\": 21052,\"fail_nums\": [258,238,351,336,243,172,108,76,35,18,10,8,7,3,9,4,7,1,1,3,3,1,0,1,2,0,0,0,0,0],\"fail_total\": 1895},\"qtypename\": \"\u5bf9\u6740\u9898\",\"hasbook\": false,\"issingle\": true,\"xuandians\": [],\"sms_count\": 6,\"nexterrorurl\": \"\",\"sy\": 8,\"enable_answer\": false,\"name\": null,\"attr_type\": 0,\"ans_count\": 11,\"userid\": 1,\"taotaiid\": 0,\"is_public\": true,\"sx\": 8,\"disuse\": 3,\"isguess\": false,\"prepos\": [[\"rb\",\"rc\",\"qc\",\"pd\",\"od\",\"nc\",\"nb\",\"ra\"],[\"qa\",\"qb\",\"pc\",\"oc\",\"ob\",\"oa\",\"qd\",\"rd\",\"qf\",\"sc\"]],\"myan\": null,\"options\": [],\"levelname\": \"10K+\"};var taskinfo = null;"
    resp_text = "var g_qq = {\"status\": 2,\"pos_y1\": 0,\"pos_y2\": 12,\"islei\": false,\"myoper\": {\"mystar\": false,\"tags\": [],\"mytags\": []},\"layoutnumber\": 1,\"qshids\": [],\"userlevel\": 105,\"orgid\": 0,\"vv\": 6,\"signs\": [],\"vote\": 3.8,\"bookinfos\": [{\"pinyin\": \"\",\"bookname\": \"\u7b2c\u4e8c\u518c\u8bfe\u540e\u7ec3\u4e60\",\"nodename\": \"\u773c\u4e0e\u773c\u89d2\",\"bookid\": 25338,\"bookurl\": 25338}],\"qtype\": 16,\"id\": 138373,\"fine_status\": 4,\"points\": [],\"publicid\": 123331,\"title\": \"\u8bf7\u6807\u51fa\u9ed1\u68cb\u773c\u89d2\u7684\u4f4d\u7f6e\",\"ineb\": false,\"comments\": [{\"username\": \"w_4817716311289\",\"showcontent\": \"\u8d3c\",\"douname\": \"\",\"headpath\": \"headicon_128.png\",\"userid\": 425779,\"updated\": 1614513094,\"doustatus\": 0,\"id\": 988054,\"dou\": 0}],\"specs\": [],\"lu\": 13,\"max_levelname\": \"\",\"hasspec\": false,\"blackfirst\": true,\"luozis\": [\"cl\",\"el\"],\"username\": \"Dachen\",\"pos_x2\": 12,\"pos_x1\": 0,\"andata\": {\"0\": {\"c\": 0,\"subs\": [1,4],\"pt\": \"\",\"f\": 0,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [],\"id\": 0},\"1\": {\"c\": 0,\"subs\": [2],\"pt\": \"cl\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [818540],\"id\": 1},\"2\": {\"c\": 0,\"subs\": [3],\"pt\": \"\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 1,\"u\": 0,\"aids\": [818540],\"id\": 2},\"3\": {\"c\": 0,\"subs\": [],\"pt\": \"el\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 2,\"u\": 0,\"aids\": [818540],\"id\": 3},\"4\": {\"c\": 0,\"subs\": [5],\"pt\": \"el\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 0,\"u\": 0,\"aids\": [818542],\"id\": 4},\"5\": {\"c\": 0,\"subs\": [6],\"pt\": \"\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 4,\"u\": 0,\"aids\": [818542],\"id\": 5},\"6\": {\"c\": 0,\"subs\": [],\"pt\": \"cl\",\"f\": 1,\"tip\": \"\",\"o\": 0,\"p\": 5,\"u\": 0,\"aids\": [818542],\"id\": 6}},\"edit_count\": 3,\"answers\": [{\"username\": \"Dachen\",\"change_count\": 0,\"ty\": 3,\"nu\": 1,\"userid\": 191070,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"cl\",\"c\": \"\"},{\"p\": \"\",\"c\": \"\"},{\"p\": \"el\",\"c\": \"\"}],\"id\": 818540},{\"username\": \"Dachen\",\"change_count\": 0,\"ty\": 3,\"nu\": 2,\"userid\": 191070,\"st\": 2,\"ok_count\": 0,\"error_count\": 0,\"bad_count\": 0,\"v\": 0,\"pts\": [{\"p\": \"el\",\"c\": \"\"},{\"p\": \"\",\"c\": \"\"},{\"p\": \"cl\",\"c\": \"\"}],\"id\": 818542}],\"is_share\": true,\"min_levelname\": \"\",\"taskresult\": {\"ok_nums\": [11,17,46,119,376,419,223,170,92,48,29,12,6,5,10,3,3,2,2,1,1,1,0,0,0,0,0,0,0,0],\"ok_total\": 1596,\"fail_nums\": [2,5,10,25,34,42,21,16,8,1,3,3,2,1,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0],\"fail_total\": 175},\"qtypename\": \"\u843d\u5b50\u9898\",\"hasbook\": false,\"issingle\": true,\"xuandians\": [],\"sms_count\": 0,\"nexterrorurl\": \"\",\"sy\": 13,\"enable_answer\": true,\"name\": \"\u627e\u773c\u89d2\",\"attr_type\": 0,\"ans_count\": 2,\"userid\": 191070,\"taotaiid\": 0,\"is_public\": true,\"sx\": 13,\"disuse\": 0,\"isguess\": false,\"prepos\": [[\"cm\",\"dl\",\"em\"],[]],\"myan\": null,\"options\": [],\"levelname\": \"10K\"};var taskinfo "
    result = re.search(
        "var g_qq = (.*);var taskinfo", resp_text).group()
    result = result.replace("var g_qq = ", "")
    result = result.replace(";var taskinfo", "")
    jsonValue = json.loads(result)
    questions = jsonValue['prepos']
    size = jsonValue['lu']
    andata = jsonValue['andata']

    return questions, andata, size, jsonValue['pos_x1'], jsonValue['pos_x2']

# get_question(295223)

# [['ap', 'bp', 'cp', 'cq', 'dq', 'ar', 'dr', 'cs'], ['ao', 'bo', 'co', 'do', 'dp', 'bq', 'eq', 'br', 'er', 'ds', 'es']]
# [{'p': 'sb', 'c': ''}]

#     A B C D E F G H I  J  K  L  M  N  O  P  Q  R　S
#   S   @ X O O                                       S
#   R X O   X O                                       R
#   Q   O X X O                                       Q
#   P X X X O                                         P
#   O O O O O                                         O
#   N                                                 N
#   M                                                 M
#   L                                                 L
#   K                                                 K
#   J                                                 J
#   I                                                 I
#   H                                                 H
#   G                                                 G
#   F                                                 F
#   E                                                 E
#   D                                                 D
#   C                                                 C
#   B                                                 B
#   A                                                 A
#     A B C D E F G H I  J  K  L  M  N  O  P  Q  R　S

# endregion

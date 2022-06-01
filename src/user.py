import discord
import json

user_level = None

def get_json(path):
    global user_level
    f = open(path, 'r', encoding='utf-8')
    user_level = json.load(f)
    f.close()

def get_user_data(author):
    global user_level
    has_data = False
    for user_data in user_level:
        if user_data['user_id'] == author.id :
            has_data = True
            return user_data
    
    if has_data == False :
        user_data = { 'user_id': author.id , 'exp': 0 }
        user_level.append(user_data)
        return user_data

def add_user_exp(user_data):
    user_data['exp'] += 1

def save_json(path):
    f = open(path, 'w')
    json.dump(user_level, f, indent = 0)
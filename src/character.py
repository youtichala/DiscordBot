import discord
from discord.ui import Button, Select, View
from io import BytesIO
import src.characterGUI
import src.user
import functions.util
import config
from os.path import exists

skin_table = ['#FDFAF0', '#FEF3D1', '#FCE7DB', '#FAF0E6', '#FBD7C9', '#FFF5EE', '#FFDAB9',
              '#F0B594', '#F5DEB3', '#D2B48C', '#CD853F', '#B87333', '#D2691E', '#75542B', '#5C3E18']

blusher_table = ['#FDFAF0', '#FEF3D1', '#FCE7DB', '#FAF0E6', '#FBD7C9', '#FFF5EE', '#FFDAB9',
                 '#F0B594', '#F5DEB3', '#D2B48C', '#CD853F', '#B87333', '#D2691E', '#75542B', '#5C3E18']

hair_table = ['#FEF3D1', '#CD853F', '#D2691E', '#75542B', '#5C3E18', '#FF80BF', '#E45674',
              '#FFB366', '#FFF345', '#FFBF00', '#0093C1', '#00559A', '#4DE680', '#A72D84', '#5F2660']

wear_table = ['#FEF3D1', '#CD853F', '#D2691E', '#75542B', '#5C3E18', '#FF80BF', '#E45674',
              '#FFB366', '#FFF345', '#FFBF00', '#0093C1', '#00559A', '#4DE680', '#A72D84', '#5F2660']


async def character_action(message, msgs):
    if len(msgs) > 1:
        if msgs[1] == "詠唱":
            outlook_button = Button(
                label="顯示外觀", custom_id=str(message.author.id)+'_outlook', style=discord.ButtonStyle.gray)
            adjust_button = Button(
                label="調整外觀", custom_id=str(message.author.id)+'_adjust', style=discord.ButtonStyle.gray)
            purchase_button = Button(
                label="學習法術", custom_id=str(message.author.id)+'_purchase', style=discord.ButtonStyle.gray)

            view = View(timeout=None)
            view.add_item(outlook_button)
            view.add_item(adjust_button)
            view.add_item(purchase_button)

            outlook_button.callback = outlook_button_click
            adjust_button.callback = adjust_button_click
            purchase_button.callback = purchase_button_click

            await message.delete()
            await message.channel.send('<@'+str(message.author.id)+'> 請選擇功能', view=view)
            return True
        else:
            return False
    else:
        return False


async def outlook_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):

        character_set = get_user_data(interaction.user)

        await interaction.message.delete()
        reply = await interaction.channel.send('生成中...')

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await reply.delete()
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            level, exp, gap = calculate_exp(
                src.user.get_user_data(interaction.user)['exp'])
            await interaction.channel.send(content='畫面中浮現出 <@'+str(interaction.user.id)+'> Lv.'+str(level)+' ('+str(exp)+'/'+str(gap)+') 的倒影')
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


def get_user_data(author):
    user_data = src.user.get_user_data(author)

    if 'avatar' not in user_data:
        user_data = src.user.update_avatar_data(
            user_data, src.user.create_avatar_data())

    skin_color = functions.util.str_split(
        user_data['avatar']['skin_color'], ',')
    blusher_color = functions.util.str_split(
        user_data['avatar']['blusher_color'], ',')
    hair_color = functions.util.str_split(
        user_data['avatar']['hair_color'], ',')
    hair_decoration1_color = functions.util.str_split(
        user_data['avatar']['hair_decoration1_color'], ',')
    hair_decoration2_color = functions.util.str_split(
        user_data['avatar']['hair_decoration2_color'], ',')
    wear_decoration1_color = functions.util.str_split(
        user_data['avatar']['wear_decoration1_color'], ',')
    wear_decoration2_color = functions.util.str_split(
        user_data['avatar']['wear_decoration2_color'], ',')

    return (user_data['avatar']['gender'],
            user_data['avatar']['hair_style'],
            user_data['avatar']['wear_style'],
            skin_color,
            blusher_color,
            hair_color,
            hair_decoration1_color,
            hair_decoration2_color,
            wear_decoration1_color,
            wear_decoration2_color)


def update_user_avatar_data(user_data, avatar_data):
    return src.user.update_avatar_data(user_data, avatar_data)


async def adjust_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        gender_button = Button(
            label="性別", custom_id=str(interaction.data['custom_id'])+"_gender", style=discord.ButtonStyle.gray)
        style_button = Button(
            label="造型", custom_id=str(interaction.data['custom_id'])+"_style", style=discord.ButtonStyle.gray)
        color_button = Button(
            label="顏色", custom_id=str(interaction.data['custom_id'])+"_color", style=discord.ButtonStyle.gray)

        gender_button.callback = gender_button_click
        style_button.callback = style_button_click
        color_button.callback = color_button_click

        view = View(timeout=None)
        view.add_item(gender_button)
        view.add_item(style_button)
        view.add_item(color_button)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇項目', view=view)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def gender_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        male_button = Button(
            label="男生", custom_id=str(interaction.data['custom_id'])+"_male", style=discord.ButtonStyle.gray)
        female_button = Button(
            label="女生", custom_id=str(interaction.data['custom_id'])+"_female", style=discord.ButtonStyle.gray)

        male_button.callback = male_button_click
        female_button.callback = female_button_click

        view = View(timeout=None)
        view.add_item(male_button)
        view.add_item(female_button)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇性別', view=view)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def male_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = ('male', character_set[1], character_set[2], character_set[3], character_set[4],
                         character_set[5], character_set[6], character_set[7], character_set[8], character_set[9])
        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': 'male',
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='看呀！ <@'+str(interaction.user.id)+'> 變成男生了')
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def female_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = ('female', character_set[1], character_set[2], character_set[3], character_set[4],
                         character_set[5], character_set[6], character_set[7], character_set[8], character_set[9])
        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': 'female',
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='看呀！ <@'+str(interaction.user.id)+'> 變成女生了')
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def style_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        hair_style_button = Button(
            label="頭髮", custom_id=str(interaction.data['custom_id'])+"_hair", style=discord.ButtonStyle.gray)
        wear_style_button = Button(
            label="穿著", custom_id=str(interaction.data['custom_id'])+"_wear", style=discord.ButtonStyle.gray)

        hair_style_button.callback = hair_style_button_click
        wear_style_button.callback = wear_style_button_click

        view = View(timeout=None)
        view.add_item(hair_style_button)
        view.add_item(wear_style_button)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇部位', view=view)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_style_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='類型一', value='01'),
            discord.SelectOption(label='類型二', value='02'),
            discord.SelectOption(label='類型三', value='03'),
            discord.SelectOption(label='類型四', value='04'),
            discord.SelectOption(label='類型五', value='05'),
            discord.SelectOption(label='類型六', value='06')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = hair_style_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇造型', view=view)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_style_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        hair_style = interaction.data['values'][0]

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], hair_style, character_set[2], character_set[3], character_set[4],
                         character_set[5], character_set[6], character_set[7], character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': hair_style,
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 換一個髮型')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def wear_style_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='類型一', value='01'),
            discord.SelectOption(label='類型二', value='02'),
            discord.SelectOption(label='類型三', value='03'),
            discord.SelectOption(label='類型四', value='04'),
            discord.SelectOption(label='類型五', value='05'),
            discord.SelectOption(label='類型六', value='06')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = wear_style_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇造型', view=view)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def wear_style_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        wear_style = interaction.data['values'][0]

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], wear_style, character_set[3], character_set[4],
                         character_set[5], character_set[6], character_set[7], character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': wear_style,
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 決定換一件衣服')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def color_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        skin_button = Button(
            label="膚色", custom_id=str(interaction.data['custom_id'])+"_skin", style=discord.ButtonStyle.gray)
        blusher_button = Button(
            label="腮紅", custom_id=str(interaction.data['custom_id'])+"_blusher", style=discord.ButtonStyle.gray)
        hair_button = Button(
            label="髮色", custom_id=str(interaction.data['custom_id'])+"_hair", style=discord.ButtonStyle.gray)
        hair_decoration1_button = Button(
            label="頭飾1", custom_id=str(interaction.data['custom_id'])+"_hair_decoration1", style=discord.ButtonStyle.gray)
        hair_decoration2_button = Button(
            label="頭飾2", custom_id=str(interaction.data['custom_id'])+"_hair_decoration2", style=discord.ButtonStyle.gray)
        wear1_button = Button(
            label="衣著1", custom_id=str(interaction.data['custom_id'])+"_wear1", style=discord.ButtonStyle.gray)
        wear2_button = Button(
            label="衣著2", custom_id=str(interaction.data['custom_id'])+"_wear2", style=discord.ButtonStyle.gray)

        skin_button.callback = skin_button_click
        blusher_button.callback = blusher_button_click
        hair_button.callback = hair_button_click
        hair_decoration1_button.callback = hair_decoration1_button_click
        hair_decoration2_button.callback = hair_decoration2_button_click
        wear1_button.callback = wear1_button_click
        wear2_button.callback = wear2_button_click

        character_set = get_user_data(interaction.user)
        hair_decoration1_path = config.get_root_path() + "img/charapter/" + \
            character_set[0] + "/Hair/" + \
            character_set[1] + "/decoration-1.png"
        hair_decoration2_path = config.get_root_path() + "img/charapter/" + \
            character_set[0] + "/Hair/" + \
            character_set[1] + "/decoration-2.png"
        wear_decoration1_path = config.get_root_path() + "img/charapter/" + \
            character_set[0] + "/Wear/" + \
            character_set[2] + "/decoration-1.png"
        wear_decoration2_path = config.get_root_path() + "img/charapter/" + \
            character_set[0] + "/Wear/" + \
            character_set[2] + "/decoration-2.png"

        view = View(timeout=None)
        view.add_item(skin_button)
        view.add_item(blusher_button)
        view.add_item(hair_button)
        if exists(hair_decoration1_path):
            view.add_item(hair_decoration1_button)
        if exists(hair_decoration2_path):
            view.add_item(hair_decoration2_button)
        if exists(wear_decoration1_path):
            view.add_item(wear1_button)
        if exists(wear_decoration2_path):
            view.add_item(wear2_button)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇部位', view=view)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def skin_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='粉雪白', value='#FDFAF0'),
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='維納斯白', value='#FCE7DB'),
            discord.SelectOption(label='亞麻色', value='#FAF0E6'),
            discord.SelectOption(label='奶油色', value='#FBD7C9'),

            discord.SelectOption(label='海貝色', value='#FFF5EE'),
            discord.SelectOption(label='粉撲桃色', value='#FFDAB9'),
            discord.SelectOption(label='淡膚色', value='#F0B594'),
            discord.SelectOption(label='小麥色', value='#F5DEB3'),
            discord.SelectOption(label='日曬色', value='#D2B48C'),

            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='古銅色', value='#B87333'),
            discord.SelectOption(label='巧克力色', value='#D2691E'),
            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='樹皮色', value='#5C3E18')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = skin_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/skin.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def skin_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        skin_color = functions.util.color_parse(interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], skin_color, character_set[4],
                         character_set[5], character_set[6], character_set[7], character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(skin_color[0])+','+str(skin_color[1])+','+str(skin_color[2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 決定換一個膚色')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def blusher_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='粉撲桃', value='#FFDAB9'),
            discord.SelectOption(label='淡膚色', value='#F0B594'),
            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='巧克力', value='#D2691E'),

            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='淡紅色', value='#FFCCCB'),
            discord.SelectOption(label='亮珊瑚', value='#F08080'),
            discord.SelectOption(label='蕃茄紅', value='#FF6347'),
            discord.SelectOption(label='緋紅色', value='#DC143C'),

            discord.SelectOption(label='粉紅色', value='#FFC0CB'),
            discord.SelectOption(label='粉紫色', value='#E45674'),
            discord.SelectOption(label='山茶紅', value='#E63995'),
            discord.SelectOption(label='蜜橙色', value='#FFB366'),
            discord.SelectOption(label='珊瑚紅', value='#FF7F50')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = blusher_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/blusher.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def blusher_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        blusher_color = functions.util.color_parse(
            interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], character_set[3], blusher_color,
                         character_set[5], character_set[6], character_set[7], character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(blusher_color[0])+','+str(blusher_color[1])+','+str(blusher_color[2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 有了更好看的腮紅了')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='巧克力色', value='#D2691E'),
            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='樹皮色', value='#5C3E18'),

            discord.SelectOption(label='淺珊瑚紅', value='#FF80BF'),
            discord.SelectOption(label='粉紫色', value='#E45674'),
            discord.SelectOption(label='蜜橙色', value='#FFB366'),
            discord.SelectOption(label='鮮黃色', value='#FFF345'),
            discord.SelectOption(label='琥珀色', value='#FFBF00'),

            discord.SelectOption(label='天藍色', value='#0093C1'),
            discord.SelectOption(label='孔雀藍色', value='#00559A'),
            discord.SelectOption(label='綠松石色', value='#4DE680'),
            discord.SelectOption(label='薰衣草紫', value='#A72D84'),
            discord.SelectOption(label='紫杜鵑色', value='#5F2660')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = hair_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/hair.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        hair_color = functions.util.color_parse(interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], character_set[3], character_set[4],
                         hair_color, character_set[6], character_set[7], character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(hair_color[0])+','+str(hair_color[1])+','+str(hair_color[2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 剛剛染了新髮色')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_decoration1_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='巧克力色', value='#D2691E'),
            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='樹皮色', value='#5C3E18'),

            discord.SelectOption(label='淺珊瑚紅', value='#FF80BF'),
            discord.SelectOption(label='粉紫色', value='#E45674'),
            discord.SelectOption(label='蜜橙色', value='#FFB366'),
            discord.SelectOption(label='鮮黃色', value='#FFF345'),
            discord.SelectOption(label='琥珀色', value='#FFBF00'),

            discord.SelectOption(label='天藍色', value='#0093C1'),
            discord.SelectOption(label='孔雀藍色', value='#00559A'),
            discord.SelectOption(label='綠松石色', value='#4DE680'),
            discord.SelectOption(label='薰衣草紫', value='#A72D84'),
            discord.SelectOption(label='紫杜鵑色', value='#5F2660')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = hair_decoration1_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/hair.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_decoration1_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        hair_decoration1 = functions.util.color_parse(
            interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], character_set[3], character_set[4],
                         character_set[5], hair_decoration1, character_set[7], character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(hair_decoration1[0])+','+str(hair_decoration1[1])+','+str(hair_decoration1[2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 換了頭飾的顏色，真好看')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_decoration2_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='巧克力色', value='#D2691E'),
            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='樹皮色', value='#5C3E18'),

            discord.SelectOption(label='淺珊瑚紅', value='#FF80BF'),
            discord.SelectOption(label='粉紫色', value='#E45674'),
            discord.SelectOption(label='蜜橙色', value='#FFB366'),
            discord.SelectOption(label='鮮黃色', value='#FFF345'),
            discord.SelectOption(label='琥珀色', value='#FFBF00'),

            discord.SelectOption(label='天藍色', value='#0093C1'),
            discord.SelectOption(label='孔雀藍色', value='#00559A'),
            discord.SelectOption(label='綠松石色', value='#4DE680'),
            discord.SelectOption(label='薰衣草紫', value='#A72D84'),
            discord.SelectOption(label='紫杜鵑色', value='#5F2660')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = hair_decoration2_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/hair.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def hair_decoration2_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        hair_decoration2 = functions.util.color_parse(
            interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], character_set[3], character_set[4],
                         character_set[5], character_set[6], hair_decoration2, character_set[8], character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(hair_decoration2[0])+','+str(hair_decoration2[1])+','+str(hair_decoration2[2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 換了頭飾的顏色，真好看')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def wear1_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='巧克力色', value='#D2691E'),
            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='樹皮色', value='#5C3E18'),

            discord.SelectOption(label='淺珊瑚紅', value='#FF80BF'),
            discord.SelectOption(label='粉紫色', value='#E45674'),
            discord.SelectOption(label='蜜橙色', value='#FFB366'),
            discord.SelectOption(label='鮮黃色', value='#FFF345'),
            discord.SelectOption(label='琥珀色', value='#FFBF00'),

            discord.SelectOption(label='天藍色', value='#0093C1'),
            discord.SelectOption(label='孔雀藍色', value='#00559A'),
            discord.SelectOption(label='綠松石色', value='#4DE680'),
            discord.SelectOption(label='薰衣草紫', value='#A72D84'),
            discord.SelectOption(label='紫杜鵑色', value='#5F2660')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = wear1_button_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/hair.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def wear1_button_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        wear1 = functions.util.color_parse(
            interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], character_set[3], character_set[4],
                         character_set[5], character_set[6], character_set[7], wear1, character_set[9])

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(wear1[0])+','+str(wear1[1])+','+str(wear1[2]),
            'wear_decoration2_color': str(character_set[9][0])+','+str(character_set[9][1])+','+str(character_set[9][2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 選了新的衣服顏色，好漂亮呀')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def wear2_button_click(interaction):
    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()

        select = Select(options=[
            discord.SelectOption(label='淡杏仁', value='#FEF3D1'),
            discord.SelectOption(label='秘魯色', value='#CD853F'),
            discord.SelectOption(label='巧克力色', value='#D2691E'),
            discord.SelectOption(label='橄欖色', value='#75542B'),
            discord.SelectOption(label='樹皮色', value='#5C3E18'),

            discord.SelectOption(label='淺珊瑚紅', value='#FF80BF'),
            discord.SelectOption(label='粉紫色', value='#E45674'),
            discord.SelectOption(label='蜜橙色', value='#FFB366'),
            discord.SelectOption(label='鮮黃色', value='#FFF345'),
            discord.SelectOption(label='琥珀色', value='#FFBF00'),

            discord.SelectOption(label='天藍色', value='#0093C1'),
            discord.SelectOption(label='孔雀藍色', value='#00559A'),
            discord.SelectOption(label='綠松石色', value='#4DE680'),
            discord.SelectOption(label='薰衣草紫', value='#A72D84'),
            discord.SelectOption(label='紫杜鵑色', value='#5F2660')
        ],
            custom_id=str(interaction.data['custom_id'])+"_select")

        cancel_btn = Button(label="取消", custom_id=str(
            interaction.data['custom_id'])+"_cancel", style=discord.ButtonStyle.gray)

        select.callback = wear2_select_click
        cancel_btn.callback = cancel_button_click

        view = View(timeout=None)
        view.add_item(select)
        view.add_item(cancel_btn)

        await interaction.channel.send('<@'+str(interaction.user.id)+'> 請選擇顏色', view=view, file=discord.File(config.get_root_path() + 'img/charapter/utility/hair.png'))
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def wear2_select_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        wear2 = functions.util.color_parse(
            interaction.data['values'][0])

        reply = await interaction.channel.send('生成中...')
        character_set = get_user_data(interaction.user)
        character_set = (character_set[0], character_set[1], character_set[2], character_set[3], character_set[4],
                         character_set[5], character_set[6], character_set[7], character_set[8], wear2)

        user_data = src.user.get_user_data(interaction.user)
        update_user_avatar_data(user_data, {
            'gender': character_set[0],
            'hair_style': character_set[1],
            'wear_style': character_set[2],
            'skin_color': str(character_set[3][0])+','+str(character_set[3][1])+','+str(character_set[3][2]),
            'blusher_color': str(character_set[4][0])+','+str(character_set[4][1])+','+str(character_set[4][2]),
            'hair_color': str(character_set[5][0])+','+str(character_set[5][1])+','+str(character_set[5][2]),
            'hair_decoration1_color': str(character_set[6][0])+','+str(character_set[6][1])+','+str(character_set[6][2]),
            'hair_decoration2_color': str(character_set[7][0])+','+str(character_set[7][1])+','+str(character_set[7][2]),
            'wear_decoration1_color': str(character_set[8][0])+','+str(character_set[8][1])+','+str(character_set[8][2]),
            'wear_decoration2_color': str(wear2[0])+','+str(wear2[1])+','+str(wear2[2])})

        with BytesIO() as image_binary:
            create_character(character_set).save(image_binary, 'PNG')
            image_binary.seek(0)
            await interaction.channel.send(file=discord.File(fp=image_binary, filename='charact.png'))
            await reply.delete()
            await interaction.channel.send(content='<@'+str(interaction.user.id)+'> 選了新的衣服顏色，好漂亮呀')

    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def purchase_button_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
        await interaction.response.send_message('尚未開放', ephemeral=True)
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


async def cancel_button_click(interaction):

    if (str(interaction.user.id)) in str(interaction.data['custom_id']):
        await interaction.message.delete()
    else:
        await interaction.response.send_message('只有呼叫功能的人可以使用', ephemeral=True)


def create_character(character_set):
    gender = character_set[0]
    hair_style = character_set[1]
    wear_style = character_set[2]
    skin_color = character_set[3]
    blusher_color = character_set[4]
    hair_color = character_set[5]
    hair_decoration1_color = character_set[6]
    hair_decoration2_color = character_set[7]
    wear_decoration1_color = character_set[8]
    wear_decoration2_color = character_set[9]

    return src.characterGUI.create_id_card(gender, 50, 50, hair_style, wear_style, skin_color, blusher_color, hair_color, hair_decoration1_color, hair_decoration2_color, wear_decoration1_color, wear_decoration2_color)


def create_test(character_set, gender, hair_style, wear_style):
    skin_color = character_set[3]
    blusher_color = character_set[4]
    hair_color = character_set[5]
    hair_decoration1_color = character_set[6]
    hair_decoration2_color = character_set[7]
    wear_decoration1_color = character_set[8]
    wear_decoration2_color = character_set[9]
    return src.characterGUI.create_id_card(gender, 50, 50, hair_style, wear_style, skin_color, blusher_color, hair_color, hair_decoration1_color, hair_decoration2_color, wear_decoration1_color, wear_decoration2_color)


def calculate_exp(value):
    exp = value
    level = 1
    gap = 10
    while exp > gap:
        exp -= gap
        level += 1
        gap += 10

    return level, exp, gap

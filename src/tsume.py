import discord
import bot_token
from io import BytesIO
import src.leelazGoGUI
import src.request

texts = ['?', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
         'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']


async def tsume_action(message, msgs):
    if msgs[1] == "測試":
        if message.author.id == bot_token.owner:
            questions, andata, size, pos_x1, pos_x2 = get_question(
                "10K", 44315)

            with BytesIO() as image_binary:
                src.leelazGoGUI.create_image(size, 30, serialize_question(
                    questions, size), [], True, pos_x1, pos_x2).save(image_binary, 'PNG')
                image_binary.seek(0)

                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

            questions, andata, size, pos_x1, pos_x2 = get_question(
                "7K", 298786)

            with BytesIO() as image_binary:
                src.leelazGoGUI.create_image(size, 30, serialize_question(
                    questions, size), [], True, pos_x1, pos_x2).save(image_binary, 'PNG')
                image_binary.seek(0)

                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

            questions, andata, size, pos_x1, pos_x2 = get_question(
                "5K", 85491)

            with BytesIO() as image_binary:
                src.leelazGoGUI.create_image(size, 30, serialize_question(
                    questions, size), [], True, pos_x1, pos_x2).save(image_binary, 'PNG')
                image_binary.seek(0)

                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

            questions, andata, size, pos_x1, pos_x2 = get_question(
                "1K", 167578)

            with BytesIO() as image_binary:
                src.leelazGoGUI.create_image(size, 30, serialize_question(
                    questions, size), [], True, pos_x1-1, pos_x2).save(image_binary, 'PNG')
                image_binary.seek(0)

                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
    else:
        return False


def get_question(level, id):
    return src.request.get_question(level, id)


def serialize_question(question, size):
    result = []
    black_table = question[0]
    white_table = question[1]

    average_x_coord = 0
    average_y_coord = 0

    for black in black_table:
        average_x_coord += texts.index(black[0])
        average_y_coord += texts.index(black[1])
    for white in white_table:
        average_x_coord += texts.index(white[0])
        average_y_coord += texts.index(white[1])

    is_x_reverse = average_x_coord / \
        (len(black_table) + len(white_table)) < size / 2
    is_y_reverse = average_y_coord / \
        (len(black_table) + len(white_table)) < size / 2

    for black in black_table:
        if is_x_reverse:
            x_coord = size + 1 - texts.index(black[0])
        else:
            x_coord = texts.index(black[0])

        if is_y_reverse:
            y_coord = size + 1 - texts.index(black[1])
        else:
            y_coord = texts.index(black[1])
        result.append("black,"+str(x_coord)+","+str(y_coord))

    for white in white_table:
        if is_x_reverse:
            x_coord = size + 1 - texts.index(white[0])
        else:
            x_coord = texts.index(white[0])

        if is_y_reverse:
            y_coord = size + 1 - texts.index(white[1])
        else:
            y_coord = texts.index(white[1])

        result.append("white,"+str(x_coord)+","+str(y_coord))

    return result

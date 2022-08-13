from PIL import Image
import config
from os.path import exists

size_width = 0
size_height = 0


def create_id_card(gender, _size_width, _size_height, hair_style, wear_style, skin_c, blusher_c, hair_c, hair_dc1, hair_dc2, wear_dc1, waer_dc2):
    global size_width, size_height

    size_width = _size_width
    size_height = _size_height

    return create_character(gender, hair_style, wear_style, skin_c, blusher_c, hair_c, hair_dc1, hair_dc2, wear_dc1, waer_dc2)


def create_character(gender, hair_style, wear_style, skin_c, blusher_c, hair_c, hair_dc1, hair_dc2, wear_dc1, waer_dc2):
    dst = Image.new('RGBA', (128, 128))

    skin_outline_path = config.get_root_path() + "img/charapter/" + \
        gender + "/Skin/outline.png"
    skin_color_path = config.get_root_path() + "img/charapter/" + \
        gender + "/Skin/color.png"
    blusher_path = config.get_root_path() + "img/charapter/" + \
        gender + "/Skin/blusher.png"
    hair_outline_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Hair/" + hair_style + "/outline.png"
    hair_color_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Hair/" + hair_style + "/color.png"
    hair_decoration1_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Hair/" + hair_style + "/decoration-1.png"
    hair_decoration2_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Hair/" + hair_style + "/decoration-2.png"
    hair_ear_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Hair/" + hair_style + "/ear.png"
    body_color_path = config.get_root_path() + "img/charapter/" + \
        gender + "/Body/color.png"
    wear_outline_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Wear/" + wear_style + "/outline.png"
    wear_decoration1_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Wear/" + wear_style + "/decoration-1.png"
    wear_decoration2_path = config.get_root_path() + "img/charapter/" + gender + \
        "/Wear/" + wear_style + "/decoration-2.png"

    skin_outline = Image.open(skin_outline_path)
    skin_color = Image.open(skin_color_path)
    body_color = Image.open(body_color_path)
    blusher = Image.open(blusher_path)
    hair_outline = Image.open(hair_outline_path)
    hair_color = Image.open(hair_color_path)
    hair_ear = Image.open(hair_ear_path)
    wear_outline = Image.open(wear_outline_path)

    skin_color = replace_color(skin_color, 128, 128, skin_c)
    body_color = replace_color(body_color, 128, 128, skin_c)
    hair_ear = replace_color(hair_ear, 128, 128, skin_c)
    blusher = replace_color(blusher, 128, 128, blusher_c)
    hair_color = replace_color(hair_color, 128, 128, hair_c)

    if gender == 'male' and hair_style == '02':
        dst = add_image(dst, 128, 128, skin_color)
        dst = add_image(dst, 128, 128, blusher)
        dst = add_image(dst, 128, 128, skin_outline)
        dst = add_image(dst, 128, 128, body_color)

        if exists(wear_decoration1_path):
            wear_decoration1 = Image.open(wear_decoration1_path)
            wear_decoration1 = replace_color(
                wear_decoration1, 128, 128, wear_dc1)
            dst = add_image(dst, 128, 128, wear_decoration1)

        if exists(wear_decoration2_path):
            wear_decoration2 = Image.open(wear_decoration2_path)
            wear_decoration2 = replace_color(
                wear_decoration2, 128, 128, waer_dc2)
            dst = add_image(dst, 128, 128, wear_decoration2)

        dst = add_image(dst, 128, 128, wear_outline)
        dst = add_image(dst, 128, 128, hair_color)

        if exists(hair_decoration1_path):
            hair_decoration1 = Image.open(hair_decoration1_path)
            hair_decoration1 = replace_color(
                hair_decoration1, 128, 128, hair_dc1)
            dst = add_image(dst, 128, 128, hair_decoration1)

        if exists(hair_decoration2_path):
            hair_decoration2 = Image.open(hair_decoration2_path)
            hair_decoration2 = replace_color(
                hair_decoration2, 128, 128, hair_dc2)
            dst = add_image(dst, 128, 128, hair_decoration2)

        dst = add_image(dst, 128, 128, hair_ear)
        dst = add_image(dst, 128, 128, hair_outline)
    else:
        dst = add_image(dst, 128, 128, skin_color)
        dst = add_image(dst, 128, 128, blusher)
        dst = add_image(dst, 128, 128, skin_outline)
        dst = add_image(dst, 128, 128, hair_color)

        if exists(hair_decoration1_path):
            hair_decoration1 = Image.open(hair_decoration1_path)
            hair_decoration1 = replace_color(
                hair_decoration1, 128, 128, hair_dc1)
            dst = add_image(dst, 128, 128, hair_decoration1)

        if exists(hair_decoration2_path):
            hair_decoration2 = Image.open(hair_decoration2_path)
            hair_decoration2 = replace_color(
                hair_decoration2, 128, 128, hair_dc2)
            dst = add_image(dst, 128, 128, hair_decoration2)

        dst = add_image(dst, 128, 128, hair_ear)
        dst = add_image(dst, 128, 128, hair_outline)
        dst = add_image(dst, 128, 128, body_color)

        if exists(wear_decoration1_path):
            wear_decoration1 = Image.open(wear_decoration1_path)
            wear_decoration1 = replace_color(
                wear_decoration1, 128, 128, wear_dc1)
            dst = add_image(dst, 128, 128, wear_decoration1)

        if exists(wear_decoration2_path):
            wear_decoration2 = Image.open(wear_decoration2_path)
            wear_decoration2 = replace_color(
                wear_decoration2, 128, 128, waer_dc2)
            dst = add_image(dst, 128, 128, wear_decoration2)

        dst = add_image(dst, 128, 128, wear_outline)

    dst = dst.resize((size_width, size_height))

    return dst


def replace_color(img, width, height, new_color):

    for i in range(0, width):
        for j in range(0, height):
            data = img.getpixel((i, j))

            if (data[3] == 255):
                img.putpixel((i, j),
                             (int(new_color[0]), int(new_color[1]), int(new_color[2])))
    return img


def add_image(det, width, height, img):

    for i in range(0, width):
        for j in range(0, height):
            data = img.getpixel((i, j))

            if (data[3] == 255):
                det.putpixel((i, j),
                             (data[0], data[1], data[2]))
    return det

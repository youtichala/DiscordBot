from PIL import Image, ImageDraw, ImageFont
import config


def decode_board_data(board_output_list):
    list_result = board_output_list.split(',')
    return list_result[0], int(list_result[1]), int(list_result[2])


def create_board(size, shift, img):
    img1 = ImageDraw.Draw(img)
    width = (size + 2) * shift
    height = (size + 2) * shift
    count_x = 1

    while count_x <= size:
        shape = [(shift * count_x + (shift * 0.5), shift * 1.5),
                 (shift * count_x + (shift * 0.5), height - (shift * 1.5))]
        img1.line(shape, fill="#000000", width=int(shift/10))
        count_x += 1
    count_x = 1

    while count_x <= size:
        shape = [(shift * 1.5, shift * count_x + (shift * 0.5)),
                 (width - (shift * 1.5), shift * count_x + (shift * 0.5))]
        img1.line(shape, fill="#000000", width=int(shift/10))
        count_x += 1

    if size == 19:
        star_x = 4
        while star_x <= 16:
            star_y = 4
            while star_y <= 16:
                img1.ellipse((shift * star_x - shift / 7 + (shift * 0.5),
                              shift * star_y - shift / 7 + (shift * 0.5),
                              shift * star_x + shift / 5 + (shift * 0.5),
                              shift * star_y + shift / 5 + (shift * 0.5)), fill='black')
                star_y += 6
            star_x += 6

    elif size == 13:
        star_x = 4
        while star_x <= 10:
            star_y = 4
            while star_y <= 10:
                img1.ellipse((shift * star_x - shift / 7 + (shift * 0.5),
                              shift * star_y - shift / 7 + (shift * 0.5),
                              shift * star_x + shift / 5 + (shift * 0.5),
                              shift * star_y + shift / 5 + (shift * 0.5)), fill='black')
                star_y += 6
            star_x += 6
        img1.ellipse((shift * 7 - shift / 7 + (shift * 0.5),
                      shift * 7 - shift / 7 + (shift * 0.5),
                      shift * 7 + shift / 5 + (shift * 0.5),
                      shift * 7 + shift / 5 + (shift * 0.5)), fill='black')

    font = ImageFont.truetype(
        config.get_root_path() + 'data/LTMuseum-Bold.ttf', 24)
    texts = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J',
             'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
    index = 1
    for text in texts:
        img1.text((index * shift + (shift * 0.5), height * (1 - 0.02 * 19.0/size)), text,
                  font=font, align="center", anchor="ms", fill='black')
        img1.text((index * shift + (shift * 0.5), height * 0.045 * 19.0 / size),
                  text, font=font, align="center", anchor="ms", fill='black')
        index += 1
        if index > size:
            break

    index = 1
    while index <= size:
        img1.text((shift * 0.6, index * shift + shift * 0.7), str(size + 1 -
                  index), font=font, align="center", anchor="ms", fill='black')
        img1.text((shift * (size + 1.4), index * shift + shift * 0.7),
                  str(size + 1 - index), font=font, align="center", anchor="ms", fill='black')
        index += 1

    return img1


def create_chess(img1, size, shift, board_output_lists, history_list, show_text):
    visited_board = []

    index = 0
    while index < size * size:
        visited_board.append(0)
        index += 1

    for board_output_list in board_output_lists:
        color, x_coord, y_coord = decode_board_data(board_output_list)
        img1.ellipse((shift * x_coord + (shift * 0.5) - shift / 2.5, shift * (size - y_coord + 1) + (shift * 0.5) - shift / 2.5,
                      shift * x_coord + (shift * 0.5) + shift / 2.5, shift * (size - y_coord + 1) + (shift * 0.5) + shift / 2.5), fill=color)

        visited_board[(y_coord - 1) * size + x_coord] = 1

    if show_text == True:
        font = ImageFont.truetype(
            config.get_root_path() + 'data/LTMuseum-Bold.ttf', 18)
        index = 0
        while index < len(history_list):

            color = 'red'
            if history_list[index][0] == 'w':
                color = 'black'
            elif history_list[index][0] == 'b':
                color = 'white'

            x_coord = int(history_list[index][1])
            y_coord = int(history_list[index][2])

            if visited_board[(y_coord - 1) * size + x_coord] == 1:
                visited_board[(y_coord - 1) * size + x_coord] = 2
                img1.text((shift * x_coord + (shift * 0.5), shift * (size - y_coord + 1.25) + (shift * 0.5)), str(len(history_list) -
                          index), font=font, align="center", anchor="ms", fill=color)
            index += 1

    return img1


def create_image(size, shift, board_output_lists, history_list, show_text, chop_start, chop_end):
    width = (size + 2) * shift
    height = (size + 2) * shift

    img = Image.new(mode="RGB", size=(width, height), color=(232, 201, 126))

    img1 = create_board(size, shift, img)
    img1 = create_chess(img1, size, shift,
                        board_output_lists, history_list, show_text)

    img = img.crop((
        ((chop_start) / size) * width,
        (1 - (chop_end + 1) / size) * height,
        ((chop_end + 1) / size) * width,
        (1 - (chop_start) / size) * height))

    return img

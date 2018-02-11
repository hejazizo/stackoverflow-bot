# -*- coding: UTF-8 -*-
from bot_token import bot
from DB import cur, conn
import emoji
from keyboards import main_reply_keyboard, send_question_inline

def send_welcome(message):
    """This function registers user and sends welcome message."""
    # 2 Stages: Temporary User (not Enrolled Yet) - Permanent User
    check_temp_user = cur.execute('''SELECT tel_id FROM Users_Temp WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()
    check_user = cur.execute('''SELECT tel_id FROM Users WHERE tel_id = (%s)''', (message.from_user.id,)).fetchone()

    print(check_temp_user, check_user)
    if check_temp_user is None:
        ### Permanent Users First Touch
        if check_user is None:
            cur.execute('''INSERT INTO Users_Temp (tel_id, first_name, last_name, username, login_date, state)
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                        (message.from_user.id,
                         message.from_user.first_name,
                         message.from_user.last_name,
                         message.from_user.username,
                         message.date,
                         'START'))

            bot.send_message(message.from_user.id, emoji.emojize(":desktop_computer: Hi, I'm *Stackoverflow* Bot. "
                                                                 "\n:bust_in_silhouette: Enter your *Student Number* to register."), parse_mode="Markdown")
        ### Permanent Users After Login Message
        else:
            bot.send_message(message.from_user.id, emoji.emojize(":desktop_computer: *Stackoverflow* Bot"),
                             parse_mode="Markdown",
                             reply_markup=main_reply_keyboard)

            cur.execute('''UPDATE Users SET state = 'IDLE' WHERE tel_id = (%s)''', (message.from_user.id,))

    else:
        ### Temporary Users Not Registered Warning
        if check_user is None:
            bot.send_message(message.from_user.id, emoji.emojize(":warning: Not registered yet.\n"
                                                                 ":bust_in_silhouette: Enter your *Student Number* to register."),
                             parse_mode="Markdown", reply_markup=None)

        ### Permanent Users Message when they send /start command
        else:

            bot.send_message(message.from_user.id, emoji.emojize(":desktop_computer: *AUT Stackoverflow* Bot\n\n"
                                                                 ":red_triangle_pointed_down: *Latest News*\n"
                                                                 "      :paperclip: HW1: https://goo.gl/LecD5n\n"
                                                                 "      :clapper_board: Recorded Sessions: goo.gl/uVcDD4"),
                             parse_mode="Markdown",
                             reply_markup=main_reply_keyboard)

            cur.execute('''UPDATE Users SET state = 'IDLE' WHERE tel_id = (%s)''', (message.from_user.id,))


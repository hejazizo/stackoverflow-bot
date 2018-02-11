# -*- coding: UTF-8 -*-
from bot_token import bot
from DB import cur, conn
import emoji
import telebot
from keyboards import *
# from python_compile import compilefile
from variables import *
from limit_text import limit_text
from send_question import send_question
from send_answer import send_answer

def handle_message_finish(message):

    state = cur.execute('''SELECT state FROM Users WHERE tel_id = (%s)''', (message.from_user.id,)).fetchone()[0]
    ##############################
    ###     Send Questions     ###
    ##############################
    if state == 'Send Question':
        question, photo, document, document_type, document_size = \
            cur.execute('''SELECT cont_typing, photo, document, document_type, document_size FROM Users WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()

        if question is not None:
            id = cur.execute('''SELECT MAX(id) + 1 FROM Questions''').fetchone()[0]

            if id is None:
                id = 1

            cur.execute('''INSERT INTO Questions (id, tel_id, question, status, photo, document, document_type, document_size, send_date)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                        (id, message.from_user.id, question, 'OPEN', photo, document, document_type, document_size, message.date))
            question_id = cur.execute('''SELECT COUNT(id) FROM Questions''').fetchone()[0]

            ## SENDING to All Users except the questioner
            send_list = cur.execute('''SELECT tel_id FROM Users WHERE tel_id != (%s)''',
                                    (message.from_user.id,)).fetchall()
            keyboard = telebot.types.InlineKeyboardMarkup()

            question, keyboard = send_question(question_id, send_list[0][0], short=True)

            for user in send_list:
                try:
                    bot.send_message(user[0], question, reply_markup=keyboard)
                except Exception as e:
                    print('Sending Question to some users failed!', e)

            bot.send_message(message.from_user.id, emoji.emojize(':down_arrow: Question sent successfully.\n'
                            ':high_voltage: Points Received: ' + str(question_point)), reply_markup=main_reply_keyboard)

            ## SENDING a PREVIEW to the questioner
            owner_keyboard = telebot.types.InlineKeyboardMarkup()
            owner_keyboard = send_question(question_id, message.from_user.id, short=True)[1]
            bot.send_message(message.from_user.id, question, reply_markup=owner_keyboard)

            # updating points of questioner
            cur.execute('''UPDATE Users SET point = point + (%s) WHERE tel_id = (%s)''', (question_point, message.from_user.id, ))

        else:
            bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Empty Question!\n'), reply_markup=main_reply_keyboard)


    ##############################
    ###       Send Answer      ###
    ##############################
    elif state == 'Send Answer':
        cont_typing = cur.execute('''SELECT cont_typing FROM Users WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()[0]
        if cont_typing is not None:
            forwarded_question, question_owner, photo, document, document_type, document_size = cur.execute(
                '''SELECT forwarded_question, forwarded_user, photo, document, document_type, document_size FROM Users WHERE tel_id = (%s)''',
                (message.from_user.id, )).fetchone()
            answers_count = cur.execute('''SELECT count(id) FROM Answers''').fetchone()

            # to provide autoincrement as primary key is not id in Answers TABLE
            if answers_count is None:
                id = 1
            else:
                id = answers_count[0] + 1

            # Check if it's a new user or he/she previously sent an answer and is updating now
            check_answer = cur.execute('''SELECT tel_id, question_id FROM Answers WHERE tel_id = (%s) AND question_id = (%s)''',
                (message.from_user.id, forwarded_question)).fetchone()

            # INSERTING NEW ANSWER
            if check_answer is None:
                cur.execute(
                    '''INSERT INTO Answers (id, question_id, tel_id, answer, accepted_answer, send_date) VALUES (%s, %s, %s, %s, %s, %s)''',
                    (id, forwarded_question, message.from_user.id, cont_typing, 0, message.date))

                # updating points
                cur.execute('''UPDATE Users SET point = point + (%s) WHERE tel_id = (%s)''', (answer_point, message.from_user.id, ))
                bot.send_message(message.from_user.id, emoji.emojize(':down_arrow: Answer sent successfully.\n'
                                 ':high_voltage: Points Received: {0}').format(answer_point), reply_markup=main_reply_keyboard)

            # UPDATING PREVIOUSLY SENT ANSWER
            else:
                # ATTACHMENTS ARE REMOVED
                previous_answer = cur.execute('''SELECT answer FROM Answers WHERE question_id = (%s) AND tel_id = (%s)''', (forwarded_question, message.from_user.id, )).fetchone()[0]

                cur.execute('''UPDATE Answers SET answer = (%s), accepted_answer = (%s) WHERE question_id = (%s) AND tel_id = (%s)''',
                    (previous_answer + '\n\n' + cont_typing, 0, forwarded_question, message.from_user.id))

                bot.send_message(question_owner, emoji.emojize(':down_arrow: Answer Updated for #Q_{0}'.format(forwarded_question)))
                bot.send_message(message.from_user.id, emoji.emojize(':down_arrow: Answer updated successfully.'), reply_markup=main_reply_keyboard)

            # Time to update Photo and Document in Answers
            if photo is not None:
                cur.execute('''UPDATE Answers SET photo = (%s) WHERE question_id = (%s) AND tel_id = (%s)''', (photo, forwarded_question, message.from_user.id))
            if document is not None:
                cur.execute('''UPDATE Answers SET document = (%s), document_type = (%s), document_size = (%s) WHERE question_id = (%s) AND tel_id = (%s)''',
                            (document, document_type, document_size, forwarded_question, message.from_user.id))

            ### SENDING THE ANSWER
            # ANSWER OWNER

            answer, keyboard = send_answer(forwarded_question, message.from_user.id, message.from_user.id, short=True)
            bot.send_message(message.from_user.id, answer, reply_markup=keyboard)

            # QUESTION OWNER
            question_owner_keyboard = send_answer(forwarded_question, message.from_user.id, question_owner, short=True)[1]
            try:
                bot.send_message(question_owner, answer, reply_markup = question_owner_keyboard)
            except Exception as e:
                print('Sending Answer to Question Owner faild: ', e)

            # FOLLOWERs
            try:
                followers_list = cur.execute('''SELECT follower FROM Follow_Question WHERE question_id = (%s) AND follower != (%s)''',
                                             (forwarded_question, question_owner)).fetchall()
                for follower in followers_list:
                    # FOLLOWERs get the same MESSAGE as ANSWER OWNER
                    bot.send_message(follower[0], answer, reply_markup = keyboard)
            except Exception as e:
                print('Sending Answer to some FOLLOWERs failed: ', e)

        else:
            bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Empty Answer!'), reply_markup=main_reply_keyboard)


    # Sends a message to all users (restricted to admins)
    elif state == 'SEND MSG TO ALL USERS':

        msg = cur.execute('''SELECT cont_typing FROM Users WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()[0]

        if msg is not None:
            all_users = cur.execute('''SELECT tel_id FROM Users''').fetchall()

            msg = ':down_arrow: AUT Stackoverflow BOT message\n\n' + msg
            fail_counter = 0
            for user in all_users:
                try:
                    bot.send_message(user[0], emoji.emojize(msg))
                except:
                    fail_counter += 1

            bot.send_message(message.from_user.id, emoji.emojize(':white_heavy_check_mark: Message sent successfully ({0} Failurs).'.format(fail_counter)), reply_markup=main_reply_keyboard)
        else:
            bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Empty message!'), reply_markup=main_reply_keyboard)

############################################
    cur.execute('''UPDATE Users SET state = 'IDLE', cont_typing = NULL, photo = NULL, document = NULL, document_type = NULL, document_size = NULL WHERE tel_id = (%s)''', (message.from_user.id,))
    conn.commit()
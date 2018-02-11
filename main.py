# -*- coding: UTF-8 -*-
import emoji
import re
import numpy as np
import telebot
import pgdb
import time
import traceback

from send_email import send_mail
from keyboards import *
from DB import cur, conn

## Variables
from variables import *
from bot_token import bot

## Modules
from start import send_welcome
from handle_callback_query import callback_inline
from attachment import attachment

from finish_msg import handle_message_finish
from limit_text import limit_text
from send_question import send_question
from send_accepted_answer import send_accepted_answer
from send_answer import send_answer
# from python_compile import compilefile




print('ROBOT STARTED!')
admin_tel_id = 73106435



######################################################

############    CHECK THE TOKEN BEFORE RUN ###########

######################################################









####################################
####      Message handlers      ####
####################################
# callback data
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        callback_inline(call)
        conn.commit()
    except Exception as e:
        print(e)
        tb = traceback.format_exc()
        print(tb)

####################################
####         COMMANDS           ####
####################################
# START COMMAND
@bot.message_handler(commands=['start'])
def start(message):

    try:
        print('Start!')
        send_welcome(message)
        conn.commit()
    except Exception as e:
        print('Something went wrong in /start: ', e)

# RESET COMMAND
@bot.message_handler(commands=['update'])
def reset(message):
    try:
        st_num = cur.execute('''SELECT st_num FROM Users WHERE tel_id = (%s)''',
                             (message.from_user.id,)).fetchone()

        if st_num is not None:
            bot.send_message(message.from_user.id, emoji.emojize(":white_heavy_check_mark: Everything is updated now."), reply_markup=main_reply_keyboard)
            cur.execute('''UPDATE Users SET state = 'IDLE', cont_typing = NULL WHERE tel_id = (%s)''', (message.from_user.id,))
    except Exception as e:
        print('Something went wrong in /update: ', e)

# RESET COMMAND
@bot.message_handler(commands=['sendmsg'])
def reset(message):
    try:
        if message.from_user.id == admin_tel_id:
            bot.send_message(message.from_user.id, emoji.emojize(':right_arrow: Enter your message: '), reply_markup=Finish_Discard_keyboard)
            cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''', ('SEND MSG TO ALL USERS', message.from_user.id, ))
    except Exception as e:
        print('Something went wrong in /sendmsg: ', e)


# CONTACT COMMAND
@bot.message_handler(commands=['contact'])
def contact(message):
    try:
        st_num = cur.execute('''SELECT st_num FROM Users WHERE tel_id = (%s)''',
                             (message.from_user.id,)).fetchone()
        if st_num is not None:
            bot.send_message(message.from_user.id, emoji.emojize(":envelope: Contact Info:\n\n"
                            ":bust_in_silhouette: Ali Hejazi:\n        :white_small_square: @Ali_H93\n        :black_small_square: Hejazizo@ualberta.ca\n"
                            ":bust_in_silhouette: Nima Sedghiye\n        :white_small_square:  @Nima_sedghiye\n        :black_small_square: Nima.Sedghiye@gmail.com\n"
                            ":bust_in_silhouette: Hamed Hosseini\n        :white_small_square: @HMDHosseini\n        :black_small_square: hellihdhs@gmail.com"), reply_markup=next_page_contact)
    except Exception as e:
        print('Something went wrong in /contact: ', e)


#***************************************#
#******      PHOTO/DOCUMENT       ******#
#***************************************#
@bot.message_handler(content_types=['photo', 'document'])
def photo_doc(message):
    try:
        attachment(message)
        conn.commit()
    except Exception as e:
        print('Error in photo/document content: ', e)

#***************************************#
#******         TEXTS             ******#
#***************************************#
@bot.message_handler(func=lambda message: True)
def chat(message):
    # print(emoji.demojize(message.text))

    try:
        state = cur.execute('''SELECT state FROM Users WHERE tel_id = (%s)''',
                                         (message.from_user.id,)).fetchone()
        if state is not None:
            state = state[0]
            ####################################
            ####            IDLE            ####
            ####################################
            if state == 'IDLE':

                # SEND QUESTION
                if emoji.demojize(message.text) == ':question_mark: Send Question':
                    bot.send_message(message.from_user.id, emoji.emojize(
                        ':right_arrow: Send your question, then select Finish.\n\n'
                        ':paperclip: 1 File and 1 Photo are allowed as attachment.'),
                                     reply_markup=Finish_Discard_keyboard)
                    cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''',
                                ('Send Question', message.from_user.id))

                # MY PROFILE
                elif emoji.demojize(message.text) == ':bust_in_silhouette: My Profile':
                    try:
                        ## FIRSTNAME, LASTNAME, USERNAME
                        user = emoji.emojize(":bust_in_silhouette: " + message.from_user.first_name)
                        if message.from_user.last_name is not None:
                            user = user + message.from_user.last_name
                        if message.from_user.username is not None:
                            user = user + " (@{0})".format(message.from_user.username)

                        role, st_num = cur.execute('''SELECT role, st_num from Users WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()
                        user = user + '\n' + emoji.emojize(':white_small_square:' ) + '{0} ({1})'.format(role.capitalize(), st_num)

                        ## GETTING QUESTIONS
                        my_questions = cur.execute('''SELECT id FROM Questions WHERE tel_id = (%s) ORDER BY id''',
                                                (message.from_user.id,)).fetchall()
                        if len(my_questions) > 0:
                            ### template
                            questions = ':question_mark: Questions:'
                            ### counter is for printing three questions in each row
                            counter = 0
                            for question in my_questions:
                                if counter % 3 == 0:
                                    questions = questions + '\n'


                                # LIKE is disabled now
                                # like_number = cur.execute('''SELECT count(*) FROM Like_Question WHERE question_id = (%s)''', (question[0], )).fetchone()[0]
                                # if like_number > 0:
                                #     questions += '#Q_{0} ({1}:red_heart:)  '.format(question[0], like_number)
                                # else:
                                #     questions += '#Q_{0}  '.format(question[0])

                                counter = counter + 1
                        else:
                            questions = ':question_mark: Questions:\nNone'

                        ## GETTING ANSWERS
                        my_answers = cur.execute('''SELECT question_id, accepted_answer, rate_answer FROM Answers WHERE tel_id = (%s) ORDER BY question_id''',
                                                    (message.from_user.id,)).fetchall()
                        if len(my_answers) > 0:
                            ### counter is just to format the output by 3 in each row
                            counter = 0
                            answers = ':bright_button: Answers:'
                            for answer in my_answers:
                                if counter % 3 == 0:
                                    answers = answers + '\n'
                                if answer[1] == 0:
                                    answers += ':bright_button:#A_{0}  '.format(answer[0])
                                else:
                                    answers += ':white_heavy_check_mark:#A_{0} ({1}/5)  '.format(answer[0], answer[2])
                                counter = counter + 1

                        else:
                            answers = ':bright_button: Answers:\nNone'

                        ## TOTAL POINT calculation
                        point = 0

                        ## POINTS OF QUESTIONS AND ANSWERS
                        user_questions_count = cur.execute('''SELECT COUNT(id) FROM Questions WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()[0]
                        user_answers_count = cur.execute('''SELECT COUNT(question_id) FROM Answers WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()[0]
                        point = point + user_questions_count * question_point + user_answers_count * answer_point

                        ## POINTS OF ACCEPTED ANSWERS
                        user_accepted_answers = cur.execute('''SELECT rate_answer FROM Answers WHERE tel_id = (%s) AND accepted_answer = 1''', (message.from_user.id, )).fetchall()
                        for rate_answer in user_accepted_answers:
                            try:
                                point = point + rate_answer[0]/5.0*accepted_answer_point
                            except Exception as e:
                                print('There are some Accepted bot not Rated ANSWERs in Database!')

                        ## GETTING HIGHEST POINT
                        highest_point = cur.execute('''SELECT MAX(point) FROM Users''').fetchone()[0]
                        point = ':high_voltage: Points: {0}\n:high_voltage: Highest Point: {1}'.format(point, highest_point)

                        bot.send_message(message.from_user.id, emoji.emojize('\n\n'.join([user, questions, answers, point])), reply_markup=getfile_keyboard)

                    except Exception as e:
                        print('Something went wrong in My Profile of user: {0}'.format(message.from_user.id), e)
                        tb = traceback.format_exc()
                        print(tb)

                        bot.send_message(message.from_user.id, tb)
                        bot.send_message(admin_tel_id, 'Something went wrong in My Profile of user: {0}'.format(message.from_user.id))
                        bot.send_message(admin_tel_id, tb)

                # ALL QUESTIONS AND THEIR ANSWERS
                elif emoji.demojize(message.text) == ':page_facing_up: All Questions':
                    all_questions = cur.execute('''SELECT id, status FROM Questions ORDER BY id DESC LIMIT 10''').fetchall()
                    all_questions_count = cur.execute('''SELECT count(*) FROM Questions''').fetchone()[0]
                    questions = emoji.emojize(':page_facing_up: Total Questions: {0}\n\n'
                                              ':down_arrow: Recently Sent:\n'.format(all_questions_count))

                    if len(all_questions) > 0:

                        for question in all_questions:
                            question_id, question_state = question[0], question[1]
                            answers_count = cur.execute('''SELECT count(question_id) FROM Answers WHERE question_id = (%s)''',
                                            (question_id,)).fetchone()[0]
                            questions += emoji.emojize(':question_mark:#Q_') + "{0} - {1} Answer(s) - {2}\n".format(question_id, answers_count, question_state)
                    else:
                        questions += 'None'

                    # TOP Questions is disabled now
                    # questions += emoji.emojize('\n:down_arrow: Top Questions:\n')
                    # best_questions = cur.execute('''SELECT question_id, count(liked_by) FROM Like_Question GROUP BY question_id ORDER BY count(liked_by) DESC, question_id DESC LIMIT 3''').fetchall()
                    # for question in best_questions:
                    #     question_id = question[0]
                    #     like_number = question[1]
                    #     questions += emoji.emojize(':question_mark: #Q_{0} ({1}:red_heart:)\n'.format(question_id, like_number))

                    bot.send_message(message.from_user.id, questions, reply_markup=getfile_keyboard)

                # OPEN QUESTIONS
                elif emoji.demojize(message.text) == ':question_mark: Open Questions':
                    open_questions_list = cur.execute('''SELECT id FROM Questions WHERE status = (%s) ORDER BY id''',
                                                      ('OPEN',)).fetchall()
                    questions = emoji.emojize(':question_mark: Open Questions: ')
                    if len(open_questions_list) > 0:
                        for question in open_questions_list:
                            answers_count = \
                            cur.execute('''SELECT count(question_id) FROM Answers WHERE question_id = (%s)''',
                                        (question[0],)).fetchone()[0]
                            questions += "\n#Q_{0} - {1} Answer(s)".format(question[0], answers_count)
                    else:
                        questions +='None'

                    bot.send_message(message.from_user.id, questions)


                ### TOP STUDENTS
                elif emoji.demojize(message.text) == ':high_voltage: Top Students':
                    msg_text = emoji.emojize('\n:down_arrow: Top 5 Students:\n\n')
                    best_students = cur.execute(
                        '''SELECT st_num, first_name, last_name, point, tel_id FROM Users ORDER BY point DESC LIMIT 5''').fetchall()

                    for student in best_students:
                        try:
                            student_id = student[0]
                            first_name = student[1]
                            last_name = student[2]
                            if last_name is None:
                                last_name = ''
                            point = student[3]
                            tel_id = student[4]

                            questions_num = cur.execute('''SELECT COUNT(id) FROM Questions WHERE tel_id = (%s)''', (tel_id, )).fetchone()[0]
                            answers_num = cur.execute('''SELECT COUNT(question_id) FROM Answers WHERE tel_id = (%s)''', (tel_id, )).fetchone()[0]
                            accepted_answers_num = cur.execute('''SELECT COUNT(question_id) FROM Answers WHERE tel_id = (%s) AND accepted_answer = 1''', (tel_id, )).fetchone()[0]

                            msg_text += emoji.emojize(
                                ':bust_in_silhouette: {0} - {1} {2} \n'
                                ':question_mark: {3}, :bright_button: {4}, :white_heavy_check_mark: {5} \n:high_voltage: {6} points\n\n'.format(student_id, first_name, last_name, questions_num, answers_num, accepted_answers_num, point))
                        except Exception as e:
                            print(e)

                    bot.send_message(message.from_user.id, msg_text)

                ### BY PRESSING A NUMBER, IT'S QUESTION WILL POP UP (IF ACCEPTED ANSWER IS READY, THAT WILL COME TOO)
                else:
                    # Check if entered only a number
                    q_pattern = r'^(?P<question_id>\d+)$'
                    q_res = re.match(q_pattern, message.text)

                    if q_res is not None:
                        question_id = q_res.group('question_id')
                        id = cur.execute('''SELECT id FROM Questions WHERE id = (%s)''', (question_id,)).fetchone()

                        # Check if number matches a question
                        if id is not None:
                            question, keyboard = send_question(question_id, message.from_user.id, short=True)
                            bot.send_message(message.from_user.id, question, reply_markup=keyboard)

                            # If Questions has accepted answer, BOT will send it too
                            question_state = cur.execute('''SELECT status FROM Questions WHERE id = (%s)''', (id, )).fetchone()[0]
                            if question_state != 'REPORTED':
                                answer_owners = cur.execute('''SELECT tel_id FROM Answers WHERE question_id = (%s) AND accepted_answer = 1''', (question_id, )).fetchall()
                                if len(answer_owners) > 0:
                                    for answer_owner in answer_owners:
                                        answer_owner = answer_owner[0]
                                        answer, keyboard = send_answer(question_id, answer_owner, message.from_user.id, short=True)

                                        if answer is not None:
                                            bot.send_message(message.from_user.id, answer, reply_markup=keyboard)


                            admins_answers = cur.execute('''SELECT answer, Answers.tel_id FROM Answers, Users WHERE Answers.tel_id = Users.tel_id AND
question_id = (%s) AND Users.role = (%s)''', (question_id, 'ADMIN')).fetchall()

                            for answer in admins_answers:
                                answer, keyboard = send_answer(question_id, answer[1], message.from_user.id, short=True)
                                bot.send_message(message.from_user.id, answer, reply_markup=keyboard)

                        else:
                            # Message when number is beyond total questions
                            total_questions_number = cur.execute('''SELECT count(id) FROM Questions''').fetchone()[0]
                            bot.send_message(message.from_user.id, emoji.emojize(
                                ':right_arrow: Number exceeded total questions.\n\n:question_mark: *Total Questions: {0}*'
                                    .format(total_questions_number)), parse_mode='Markdown')

                    # ADD OR REMOVE A USER
                    else:
                        ## ADDING A USER
                        if message.from_user.username in admins:
                            add_pattern = r'^add (?P<stnum>\d{1,30}) (?P<role>\w+)$'
                            add_res = re.match(add_pattern, message.text, re.IGNORECASE)

                            if add_res is not None:
                                st_num = add_res.group('stnum')
                                role = add_res.group('role').upper()
                                check_stnum = cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (st_num, )).fetchone()

                                ### CHECKING FOR VALID ROLES SUCH AS STUDENT, TA, ETC
                                if role in valid_roles:
                                    if check_stnum is None:
                                        cur.execute('''INSERT INTO Users (st_num, role) VALUES (%s, %s)''', (st_num, role))
                                        bot.send_message(message.from_user.id, emoji.emojize(":white_heavy_check_mark: Student Number *{0}* "
                                                         "added with role *{1}*.".format(st_num, role)), parse_mode='Markdown')
                                    else:
                                        bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Student Number {0} is already added.'.format(st_num)))
                                else:
                                    bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Invalid role *{0}*.'.format(role)), parse_mode='Markdown')
                            ## REMOVING A USER
                            else:
                                remove_pattern = r'^remove (?P<st_num>\d{1,30})$'
                                remove_res = re.match(remove_pattern, message.text, re.IGNORECASE)

                                if remove_res is not None:
                                    st_num = remove_res.group('st_num')
                                    check_stnum = cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''',
                                                              (st_num,)).fetchone()

                                    if check_stnum is not None:
                                        check_role = cur.execute('''SELECT role FROM Users WHERE st_num = (%s)''', (st_num, )).fetchone()[0]
                                        if check_role in ['ADMIN']:
                                            bot.send_message(message.from_user.id, emoji.emojize(
                                                ':cross_mark: Cannot remove *{0}s*.'.format(check_role)), parse_mode='Markdown')
                                        else:
                                            cur.execute('''DELETE FROM Users WHERE st_num = (%s) AND role NOT IN (%s)''',
                                                        (st_num, 'ADMIN'))
                                            cur.execute('''DELETE FROM Users_Temp WHERE st_num = (%s)''',
                                                (st_num, ))
                                            bot.send_message(message.from_user.id, emoji.emojize(
                                                ':white_heavy_check_mark: Student Number *{0}* removed.'.format(st_num)), parse_mode='Markdown')
                                    else:
                                        bot.send_message(message.from_user.id, emoji.emojize(
                                            ':cross_mark: Student Number {0} is already removed.'.format(st_num)))



            ####################################
            ####         Rate Answer        ####
            ####################################
            elif state == 'Rate Answer':

                pattern = r"(^(:bright_button:){1,5}$)"
                res = re.match(pattern, emoji.demojize(message.text))
                if res is not None:
                    rate = len(res.group(0).split("::"))

                    # Question and Answer Owner
                    forwarded_question, forwarded_user = cur.execute(
                        '''SELECT forwarded_question, forwarded_user FROM Users WHERE tel_id = (%s)''',
                        (message.from_user.id,)).fetchone()

                    cur.execute('''UPDATE Answers SET rate_answer = (%s) WHERE question_id = (%s) AND tel_id = (%s)''',
                                (rate, forwarded_question, forwarded_user))

                    bot.send_message(message.from_user.id, emoji.emojize(":white_heavy_check_mark: Thanks! Answer rated *{0}*.".format(rate)), reply_markup=main_reply_keyboard, parse_mode='Markdown')
                    bot.send_message(forwarded_user, emoji.emojize(
                        ':white_heavy_check_mark: Your answer for #Q_{0} accepted and rated {1}.\n'
                        ':high_voltage: Points Received: {2}'.format(forwarded_question, rate, accepted_answer_point*rate/5.0)))

                    # RESETING STATE TO IDLE
                    cur.execute('''UPDATE Users SET state = (%s)  WHERE tel_id = (%s)''', ('IDLE', message.from_user.id))
                    # Increasing point of answer owner
                    cur.execute('''UPDATE Users SET point = point + (%s) WHERE tel_id = (%s)''', (accepted_answer_point*rate/5.0, forwarded_user))



                else:
                    bot.reply_to(message, emoji.emojize(":cross_mark: Invalid input."))


            ####################################
            ####        Send Question       ####
            ####################################
            elif state in ['Send Question', 'Send Answer']:
                # FINISH KEY
                if emoji.demojize(message.text) == ':white_heavy_check_mark: Finish':
                    handle_message_finish(message)

                # DISCARD KEY
                elif emoji.demojize(message.text) == ':cross_mark: Discard':
                    # RESETING TO IDLE
                    cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''', ('IDLE', message.from_user.id))
                    cur.execute('''UPDATE Users SET cont_typing = NULL, photo = NULL, document = NULL, document_type = NULL,
document_size = NULL WHERE tel_id = (%s)''', (message.from_user.id, ))
                    bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Discarded.'), reply_markup=main_reply_keyboard)
                    conn.commit()

                # CONTINUE TYPING ANSWER OR QUESTION
                else:
                    cont_typing = cur.execute('''SELECT cont_typing FROM Users WHERE tel_id = (%s)''',
                                                      (message.from_user.id,)).fetchone()[0]
                    if cont_typing == None:
                        cur.execute('''UPDATE Users SET cont_typing = (%s) WHERE tel_id = (%s)''',
                                    (message.text, message.from_user.id))
                    else:
                        cont_typing = cur.execute('''SELECT cont_typing FROM Users WHERE tel_id = (%s)''',
                                                          (message.from_user.id,)).fetchone()[0]
                        cur.execute('''UPDATE Users SET cont_typing=(%s) WHERE tel_id = (%s)''',
                                    (cont_typing + '\n' + message.text, message.from_user.id))

            ### SENDING GLOBAL MESSAGE TO ALL USERS (RESTRICTED TO ADMINs)
            elif state == 'SEND MSG TO ALL USERS':
                # FINISH KEY
                if emoji.demojize(message.text) == ':white_heavy_check_mark: Finish':
                    handle_message_finish(message)

                # DISCARD KEY
                elif emoji.demojize(message.text) == ':cross_mark: Discard':
                    # RESETING TO IDLE
                    cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''', ('IDLE', message.from_user.id))
                    cur.execute('''UPDATE Users SET cont_typing = NULL, photo = NULL, document = NULL, document_type = NULL,
                document_size = NULL WHERE tel_id = (%s)''', (message.from_user.id,))
                    bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Discarded.'),
                                     reply_markup=main_reply_keyboard)

                else:
                    cur.execute('''UPDATE Users SET cont_typing = (%s) WHERE tel_id = (%s)''', (message.text, message.from_user.id, ))

        ####################################
        ####    NOT REGISTERED USERS    ####
        ####################################
        else:
            state = cur.execute('''SELECT state FROM Users_TEMP WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()
            if state is not None:
                state = state[0]
                ####################################
                ####            START           ####
                ####################################
                if state == 'START':
                    try:
                        pattern = r'^(?P<question_id>\d{1,30})$'
                        res = re.match(pattern, message.text)
                        if res.group():
                            st_num = res.groups()[0]

                            registered_st_num = cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (st_num, )).fetchone()
                            check_previously_register = cur.execute('''SELECT state FROM Users_temp WHERE st_num = (%s) AND state = (%s)''', (st_num, 'REGISTERED')).fetchone()
                            if check_previously_register is None:
                                if registered_st_num is None:
                                    bot.reply_to(message, emoji.emojize(":cross_mark: Sorry. Not a Registered Student Number."))
                                else:
                                    passwd = st_num
                                    bot.send_message(message.from_user.id, emoji.emojize(':key: Enter your password:'),
                                                     reply_markup=change_stnum_keyboard)

                                    cur.execute('''UPDATE Users_Temp SET st_num = (%s), login_code = (%s), state = (%s) WHERE tel_id = (%s)''',
                                                (st_num, passwd, 'LOGIN', message.from_user.id))
                            else:
                                bot.reply_to(message, emoji.emojize(":cross_mark: This Student Number is already registered."))

                    except Exception as e:
                        bot.reply_to(message, emoji.emojize(":cross_mark: Invalid Student Number"))
                        print(e)

                ####################################
                ####            LOGIN           ####
                ####################################
                elif state == 'LOGIN':

                    if emoji.demojize(message.text) == ':bust_in_silhouette: Change Student Number':
                        bot.send_message(message.from_user.id,
                                         emoji.emojize(":e-mail: Enter the *New Student Number* to register."),
                                         parse_mode='Markdown')
                        cur.execute('''UPDATE Users_TEMP SET state = (%s) WHERE tel_id = (%s)''',
                                    ('START', message.from_user.id,))
                    else:
                        digit = cur.execute('''SELECT login_code FROM Users_TEMP WHERE tel_id = (%s)''',
                                        (message.from_user.id,)).fetchone()[0]

                        try:
                            if int(message.text) == digit:

                                st_num = cur.execute('''SELECT st_num FROM Users_Temp WHERE tel_id = (%s)''', (message.from_user.id, )).fetchone()[0]
                                cur.execute("UPDATE Users SET tel_id=(%s), first_name=(%s), last_name=(%s), "
                                                             "username=(%s), login_date=(%s), state=(%s), point=(%s) WHERE st_num = (%s)",
                                            (message.from_user.id,
                                             message.from_user.first_name,
                                             message.from_user.last_name,
                                             message.from_user.username,
                                             message.date,
                                             'IDLE',
                                             0,
                                             st_num))

                                cur.execute('''UPDATE Users_Temp SET state = (%s) WHERE tel_id = (%s)''', ('REGISTERED', message.from_user.id))

                                Questions_N = cur.execute('''SELECT count(Questions.id) FROM Questions''').fetchone()[0]
                                Answers_N = cur.execute('''SELECT count(Answers.id) FROM Answers''').fetchone()[0]
                                Users_N = cur.execute('''SELECT count(Users.tel_id) FROM Users''').fetchone()[0]

                                bot.send_message(message.from_user.id, emoji.emojize(":desktop_computer: *Stackoverflow* Bot"),
                                                 parse_mode="Markdown", reply_markup=main_reply_keyboard)

                                bot.send_message(message.chat.id,emoji.emojize(':white_heavy_check_mark: Successfully registered!' +
                                                               '\n:white_heavy_check_mark: Access granted.'
                                                               '\n\n:bust_in_silhouette: Total Users: *' + str(Users_N) +
                                                                '*\n:question_mark: Total Questions: *' + str(Questions_N) + '*'
                                                                '\n:bright_button: Total Answers: *' + str(Answers_N) + '*'),
                                                 reply_markup=send_question_inline, parse_mode='Markdown')

                            else:
                                bot.send_message(message.from_user.id, emoji.emojize(':cross_mark: Wrong login code. Try again!'))
                        except Exception as e:
                            bot.send_message(message.chat.id, emoji.emojize(':cross_mark: Wrong login code. Try again!'))
                            print(e)

    except Exception as e:
        print('Something went wrong in chat(message) function (Main User): ', e)
        tb = traceback.format_exc()
        print(tb)

        try:
            bot.send_message(73106435, tb)
            bot.send_message(73106435, 'Something went wrong for User: {0}'.format(message.from_user.id))
        except:
            pass

    conn.commit()

bot.polling()
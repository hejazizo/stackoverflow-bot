from keyboards import *
from DB import cur, conn
from bot_token import bot
from limit_text import limit_text

def send_question(question_id, receiver_tel_id, short):

    id, question_owner, question, question_state, photo, document, document_type, document_size = \
            cur.execute('''SELECT id, tel_id, question, status, photo, document, document_type, document_size FROM Questions WHERE id = (%s)''', (question_id, )).fetchone()

    # limiting long questions and specifying keyboard
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=6)
    load_answers = telebot.types.InlineKeyboardButton(emoji.emojize(':bright_button: Load Answers'), callback_data='load_answers')


    # like question button is disabled now
    # liked_number = cur.execute('''SELECT count(*) from Like_Question WHERE question_id = (%s)''', (question_id, )).fetchone()[0]
    # if liked_number == 0:
    #     like_button = telebot.types.InlineKeyboardButton(emoji.emojize(':red_heart:'), callback_data='like_question')
    # else:
    #     like_button = telebot.types.InlineKeyboardButton(emoji.emojize('{0} :red_heart:'.format(liked_number)), callback_data='like_question')

    # GETTING ADMINS AND TAs
    # Receiver_tel_id which is different from send_answer.py -> answer_owner is used there
    role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (receiver_tel_id, )).fetchone()[0]

    # LONG QUESTIONS
    if (limit_text(question)):
        ## Sending with SHOWMORE or SHOWLESS
        if short:
            question = limit_text(question)
            showkey = showmore
        else:
            showkey = showless

        ## Setting keyboard for REGULAR Users (NOT owner or admin)
        if receiver_tel_id != question_owner:
            ### Setting keyboard for OPEN and CLOSED questions
            ## QUESTIONS are always open for ADMINs and TAs
            if (question_state == 'OPEN') or (role in ['ADMIN', 'TA']):
                if role == 'ADMIN':
                    ### ADMINs can load answers for every question any time

                    # like is now disabled
                    # keyboard.add(showkey, answer_question, like_button, load_answers, next_page_question)
                    keyboard.add(showkey, answer_question, load_answers, next_page_question)
                else:
                    # like is now disabled
                    # keyboard.add(showkey, answer_question, like_button, next_page_question)
                    keyboard.add(showkey, answer_question, next_page_question)
            else:
                keyboard.add(showkey)

        ## Setting keyboard for OWNER, only SHOWMORE and LOAD ANSWERS
        elif receiver_tel_id == question_owner:
            check_answers = cur.execute('''SELECT answer FROM Answers, Users WHERE question_id = (%s)
AND Users.tel_id = Answers.tel_id AND Users.role != (%s)''',
                                        (question_id, 'ADMIN')).fetchone()

            if check_answers is not None:
                if role in ['ADMIN']:
                    keyboard.add(showkey, answer_question, load_answers)
                else:
                    keyboard.add(showkey, load_answers)
            else:
                if role in ['ADMIN']:
                    keyboard.add(showkey, answer_question)
                else:
                    keyboard.add(showkey)

    # SHORT QUESTIONS
    else:
        ## Setting Keyboard for NOT OWNER and OPEN Questions
        if receiver_tel_id != question_owner:
            ## Even if the QUESTION is CLOSED, it is always open for ADMINs and TAs
            if (question_state == 'OPEN') or (role in ['ADMIN', 'TA']):
                if role == 'ADMIN':
                    ### ADMINs can load answers for every question any time

                    # like is disabled now
                    # keyboard.add(answer_question, like_button, load_answers, next_page_question)
                    keyboard.add(answer_question, load_answers, next_page_question)

                else:
                    # like is disabled now
                    # keyboard.add(answer_question, like_button, next_page_question)
                    keyboard.add(answer_question, next_page_question)

        ## Setting keyboard for OWNER, only SHOWMORE and LOAD ANSWERS
        elif receiver_tel_id == question_owner:
            # LOAD ANSWERS for owner
            check_answers = cur.execute('''SELECT answer FROM Answers, Users WHERE question_id = (%s)
            AND Users.tel_id = Answers.tel_id AND Users.role != (%s)''',
                                        (question_id, 'ADMIN')).fetchone()

            if check_answers is not None:
                if role in ['ADMIN']:
                    keyboard.add(answer_question, load_answers)
                else:
                    keyboard.add(load_answers)




    # Setting keyboard for ATTACHMENTs
    if photo is not None:
        keyboard.add(photo_button)
    if document is not None:
        document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: {0} ({1})'
                            .format(document_type, document_size)), callback_data='document')
        keyboard.add(document_button)

    # FORMATTING QUESTION
    question = emoji.emojize(':question_mark: #Q_') + str(question_id) + '\n\n' + question

    accepted_answers_count = cur.execute('''SELECT SUM(accepted_answer) FROM Answers WHERE question_id = (%s)''', (question_id, )).fetchone()[0]
    print(accepted_answers_count)
    if (question_state == 'CLOSED') and (accepted_answers_count == 0):
        question += emoji.emojize('\n\n:cross_mark: Question is Closed')

    question_owner_role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (question_owner, )).fetchone()[0]
    if question_owner_role in ['ADMIN', 'TA']:
        question += emoji.emojize('\n\n:bust_in_silhouette: Sent by {0}'.format(question_owner_role))

    return (question, keyboard)
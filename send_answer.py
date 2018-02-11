from keyboards import *
from DB import cur, conn
from bot_token import bot
from limit_text import limit_text

def send_answer(question_id, answer_owner, receiver_tel_id, short):

    answer = cur.execute('''SELECT answer FROM Answers WHERE question_id = (%s) AND tel_id = (%s)''', (question_id, answer_owner)).fetchone()
    keyboard = telebot.types.InlineKeyboardMarkup()

    if answer is not None:
        id, question_id, tel_id, answer, accepted_answer, rate_answer, photo, document, document_type, document_size, send_date = cur.execute(
            '''SELECT * FROM Answers WHERE question_id = (%s) AND tel_id = (%s)''',
            (question_id, answer_owner)).fetchone()

        question_owner = \
        cur.execute('''SELECT tel_id FROM Questions WHERE id = (%s)''', (question_id, )).fetchone()[0]
        # Limiting Long Questions and specifying keyboard accordingly

        # GETTING ADMINS AND TAs
        role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (answer_owner, )).fetchone()[0]

        # This flag is used at the bottom for Admin and TAs keyboard setting
        short_message_flag = False
        # Setting keyboard
        if limit_text(answer):
            short_message_flag = True
            # SHOWMORE key
            if short:
                answer = limit_text(answer)
                showkey = showmore
            else:
                showkey = showless

            if receiver_tel_id == question_owner:
                if accepted_answer:
                    keyboard.add(showkey)
                else:
                    keyboard.add(showkey, accept_answer, next_page_answer)
            else:
                # FOLLOWERs and Answer Owner only get a show more key
                keyboard.add(showkey)
        else:
            if receiver_tel_id == question_owner:
                if not accepted_answer:
                    if question_owner == receiver_tel_id:
                        keyboard.add(accept_answer, next_page_answer)

        # ATTACHMENTs
        if photo is not None:
            keyboard.add(photo_button)
        if document is not None:
            document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: {0} ({1})'
                              .format(document_type, document_size)), callback_data='document')
            keyboard.add(document_button)

        # SETTING EMOJI BASED ON ACCEPTED OR NOT ACCEPTED ANSWER
        if role in ['STUDENT', 'TA']:
            if accepted_answer:
                answer = emoji.emojize(':white_heavy_check_mark: #A_') + str(question_id) + ' #' + \
                         str(answer_owner) + '\n\n' + answer + emoji.emojize('\n\n:high_voltage: Rated: {0}/5'.format(rate_answer))

            else:
                answer = emoji.emojize(':bright_button: #A_') + str(question_id) + ' #' + str(answer_owner) + '\n\n' + answer

            if role == 'TA':
                answer += emoji.emojize('\n\n:bust_in_silhouette: Sent by ') + role

        ## ADMINs AND TAs answers are indicated with a flag
        elif role in ['ADMIN']:
            question_state = cur.execute('''SELECT status FROM Questions WHERE id = (%s)''', (question_id,)).fetchone()[0]

            # ADMIN Answers are different
            keyboard = telebot.types.InlineKeyboardMarkup()
            if short_message_flag:
                # SHOWMORE key
                if short:
                    showkey = showmore
                else:
                    showkey = showless

                keyboard.add(showkey)
            else:
                keyboard = None

            # ATTACHMENTs
            if photo is not None:
                keyboard.add(photo_button)
            if document is not None:
                document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: {0} ({1})'.format(document_type,
                                  document_size)), callback_data='document')
                keyboard.add(document_button)

            answer = emoji.emojize(':collision: #A_') + str(question_id) + ' #' + str(answer_owner) + '\n\n' \
                     + answer + emoji.emojize('\n\n:bust_in_silhouette: Sent by ') + role

    # Returning Answer and Two Keyboards
    return (answer, keyboard)
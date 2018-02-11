from keyboards import *
from DB import cur, conn
from bot_token import bot
from limit_text import limit_text

def send_accepted_answer(question_id):
    answer = cur.execute('''SELECT answer FROM Answers WHERE question_id = (%s) AND accepted_answer = 1 ORDER BY rate_answer LIMIT 1''', (question_id,)).fetchone()

    keyboard = telebot.types.InlineKeyboardMarkup()
    if answer is not None:
        answer, tel_id, photo, document, document_type, document_size = cur.execute(
            '''SELECT answer, tel_id, photo, document, document_type, document_size FROM Answers WHERE question_id = (%s) AND accepted_answer = 1 ORDER BY rate_answer LIMIT 1''',
            (question_id,)).fetchone()

        if (limit_text(answer)):
            answer = limit_text(answer)
            keyboard.add(showmore)

        if photo is not None:
            keyboard.add(photo_button)
        if document is not None:
            document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: {0} ({1})'
                              .format(document_type, document_size)), callback_data='document')
            keyboard.add(document_button)

        answer = emoji.emojize(':white_heavy_check_mark: #A_') + str(question_id) + ' #' + str(tel_id) + '\n\n' + answer

    return (answer, keyboard)
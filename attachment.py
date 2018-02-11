import emoji

from bot_token import bot
from DB import conn, cur

def attachment(message):
    state = cur.execute('''SELECT state FROM Users WHERE tel_id = (%s)''', (message.from_user.id,)).fetchone()

    if state is not None:
        # STATE[0] is the state retrieved (state is a tuple
        if state[0] in ['Send Question', 'Send Answer']:
            # PHOTO
            if message.content_type == 'photo':
                check_photo = \
                cur.execute('''SELECT photo FROM Users WHERE tel_id = (%s)''', (message.from_user.id,)).fetchone()[0]
                # ONLY 1 image is allowed
                if check_photo is None:
                    # FIRST image
                    bot.reply_to(message, emoji.emojize(':framed_picture: Image Attached.'))
                else:
                    # UPDATING image
                    bot.reply_to(message, emoji.emojize(':framed_picture: Image Attachment updated.'))

                cur.execute('''UPDATE Users SET photo = (%s) WHERE tel_id = (%s)''',
                            (message.photo[-1].file_id, message.from_user.id))
            # DOCUMENT
            elif message.content_type == 'document':
                check_document = cur.execute('''SELECT document FROM Users WHERE tel_id = (%s)''',
                                             (message.from_user.id,)).fetchone()[0]
                # ONLY 1 document is allowed
                if check_document is None:
                    # FIRST document
                    bot.reply_to(message, emoji.emojize(':paperclip: Document Attached.'))
                else:
                    # UPDATING document
                    bot.reply_to(message, emoji.emojize(':paperclip: Document Attachment updated.'))

                # FORMATING FILE SIZE
                FILE_SIZE = message.document.file_size / 1000.0
                if FILE_SIZE < 1000:
                    FILE_SIZE = '{0} KB'.format(round(FILE_SIZE))
                else:
                    FILE_SIZE = '{0:.1f} MB'.format(FILE_SIZE / 1000.0)

                cur.execute(
                    '''UPDATE Users SET document = (%s), document_type = (%s), document_size = (%s) WHERE tel_id = (%s)''',
                    (message.document.file_id, message.document.mime_type, FILE_SIZE, message.from_user.id))
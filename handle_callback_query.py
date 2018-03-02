import re
import sys
import os
import shutil
import emoji

from bot_token import bot
from DB import cur, conn
from keyboards import *
from variables import report_question_limit, report_user_limit
from variables import *

from limit_text import limit_text
from send_question import send_question
from send_answer import send_answer
from send_accepted_answer import send_accepted_answer

def callback_inline(call):

    message = call.message
    # RE patters for QUESTIONS, ANSWERS, and ACCEPTED ANSWERS
    question_pattern = ":question_mark: #Q_(\d+).*"
    answer_pattern = "(?::bright_button:|:white_heavy_check_mark:|:collision:) #A_(\d+) #(\d+).*"
    accepted_answer_pattern = ":white_heavy_check_mark: #(\d+).*"
    # GETTING RESULTS of patterns
    question_res = re.match(question_pattern, emoji.demojize(message.text), flags=re.DOTALL)
    answer_res = re.match(answer_pattern, emoji.demojize(message.text), flags=re.DOTALL)
    accepted_answer_res = re.match(accepted_answer_pattern, emoji.demojize(message.text), flags=re.DOTALL)

    question_id = None
    if question_res is not None:
        ##############################
        ###        Questions       ###
        ##############################
        question_id = question_res.groups()[0]
        forwarded_user = cur.execute('''SELECT tel_id FROM Questions WHERE id = (%s)''', (question_id,)).fetchone()[0]

        cur.execute('''UPDATE Users SET forwarded_user = (%s), forwarded_question = (%s)  WHERE tel_id = (%s)''',
                    (forwarded_user, question_id, message.from_user.id))

    elif answer_res is not None:
        ##############################
        ###         Answers        ###
        ##############################
        question_id = answer_res.groups()[0]
        forwarded_user = answer_res.groups()[1]

        cur.execute('''UPDATE Users SET forwarded_user = (%s), forwarded_question = (%s) WHERE tel_id = (%s)''',
                    (forwarded_user, question_id, message.from_user.id))

    #################################################
    ## IF A VALID RESULT FOUND BY REGULAR EXPRESSION
    if question_id is not None:
        forwarded_question = question_id
        cur.execute('''UPDATE Users SET forwarded_user = (%s), forwarded_question = (%s) WHERE tel_id = (%s)''', (forwarded_user, forwarded_question, call.from_user.id))
    #################################################



    #################################################
    ###                 CALLBACKS                 ###
    #################################################

    # Handling callback queries
    if call.message:
        forwarded_question, forwarded_user = cur.execute('''SELECT forwarded_question, forwarded_user
                                  FROM Users WHERE tel_id = (%s)''', (call.from_user.id,)).fetchone()

        ##############################
        #########   USER   ###########
        ##############################

        if call.data == 'load_answers':
            bot.answer_callback_query(callback_query_id=call.id, text="Loading Received Answers...")
            answers_list = cur.execute('''SELECT Answers.tel_id FROM Answers, Users WHERE question_id = (%s)
AND Answers.tel_id = Users.tel_id AND Users.role != (%s)''', (question_id, 'ADMIN')).fetchall()

            if len(answers_list) > 0:
                bot.send_message(call.from_user.id, emoji.emojize(':red_triangle_pointed_down: Loading *Question {0}* Answers...'
                                                                  .format(question_id)), parse_mode='Markdown')
                for answer in answers_list:
                    answer, keyboard = send_answer(question_id, answer[0], call.from_user.id, short=True)
                    # bot.send_message(call.from_user.id, answer, reply_markup=showkeyboard_keyboard)
                    bot.send_message(call.from_user.id, answer, reply_markup=keyboard)

        elif call.data == 'show_keyboard':
            bot.answer_callback_query(callback_query_id=call.id, text="Loading Full Keyboard...")
            keyboard = send_answer(question_id, forwarded_user, call.from_user.id, short=True)[1]
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard)

        elif call.data == "getfile":
            bot.answer_callback_query(callback_query_id=call.id, text="Sending File...")

            user = call.from_user.first_name
            if call.from_user.last_name is not None:
                user = call.from_user.first_name + ' ' + call.from_user.last_name
            if call.from_user.username is not None:
                user = user + ' @' + call.from_user.username

            ### GET FILE is used for both My Questions and All Questions
            # My Questions
            if emoji.demojize(message.text).startswith(':bust_in_silhouette:'):
                questions = cur.execute('''SELECT id, tel_id, question, status FROM questions WHERE tel_id = (%s) ORDER BY id DESC''',(call.from_user.id,)).fetchall()
                FILE_NAME = str(call.from_user.id) + '/Questions of ' + user + '.txt'
            # All Questions
            elif emoji.demojize(message.text).startswith(':page_facing_up:'):
                questions = cur.execute('''SELECT id, tel_id, question, status FROM questions ORDER BY id DESC''').fetchall()
                FILE_NAME = str(call.from_user.id) + '/All Questions - ' + user + '.txt'

            # Making a directory for each user
            if not os.path.exists(str(call.from_user.id)):
                os.mkdir(str(call.from_user.id))

            # Some settings for styling the output
            q_sep = '='*50
            a_sep = '-'*46

            # Output .txt file
            with open(FILE_NAME, 'w') as f:
                f.write('Requested by: ' + user + '\n\n\n')

                if len(questions) > 0:
                    for question in questions:
                        question_owner = question[1]
                        question_id = question[0]
                        question_text = question[2]
                        question_status = question[3]


                        # like_button is disabled now
                        # like_number = cur.execute('''SELECT count(*) FROM Like_Question WHERE question_id = (%s)''', (question[0],)).fetchone()[0]
                        # if question_owner == call.from_user.id:
                        #     if like_number > 0:
                        #         formatted_question = '#'+ str(question_id) + '   ' + str(question_status) + ' - Sent by: You - ' + 'Likes: {0}\n'.format(like_number) + q_sep + '\n' + question_text + '\n\n'
                        #     else:
                        #         formatted_question = '#'+ str(question_id) + '   ' + str(question_status) + ' - Sent by: You\n' + q_sep + '\n' + question_text + '\n\n'
                        #
                        # else:
                        #     formatted_question = '#'+ str(question_id) + '   ' + str(question_status) + '\n' + q_sep + '\n' + question_text + '\n\n'

                        if question_owner == call.from_user.id:
                            formatted_question = '#'+ str(question_id) + '   ' + str(question_status) + ' - Sent by: You\n' + q_sep + '\n' + question_text + '\n\n'
                        else:
                            formatted_question = '#'+ str(question_id) + '   ' + str(question_status) + '\n' + q_sep + '\n' + question_text + '\n\n'
                        f.write(q_sep + '\n' + formatted_question)

                        ### ANSWERs OF each QUESTION

                        # This sorts the answer by role (Admins first, then students, then TAs [alphabetical] and then
                        # based on accepted or not accepted)
                        user_answers = cur.execute(
                            '''SELECT Answers.tel_id, answer, accepted_answer, rate_answer, role FROM Answers, Users WHERE
question_id = (%s) AND Answers.tel_id = Users.tel_id ORDER BY role DESC, accepted_answer DESC''',
                            (question[0],)).fetchall()


                        if len(user_answers) > 0:
                            answer_section = a_sep + '\n' + '-'*13 + '     Answers     ' + '-'*13
                            answer_section = '\t'.join(('\n' + answer_section.lstrip()).splitlines(True))
                            f.write(answer_section)

                        for answer in user_answers:


                            answer_owner = answer[0]
                            answer_text = answer[1]
                            accepted_answer = answer[2]
                            rate = answer[3]
                            role = answer[4]

                            if accepted_answer:
                                status = 'Accepted - Rated '+ str(answer[3]) + '/5'.format(answer[3])
                            else:
                                status = 'Not Accepted'

                            question_owner_role = \
                            cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (question_owner,)).fetchone()[0]

                            ## If a Question is sent by ADMIN only accepted answers will be shown
                            if (question_owner_role in vip) and not accepted_answer:
                                continue

                            if role == 'ADMIN':
                                if answer_owner == call.from_user.id:
                                    answer = a_sep+ '\nSent by: You (ADMIN)' + '\n' + a_sep + '\n' + answer_text
                                else:
                                    answer = a_sep + '\nSent by: ADMIN (#' + str(answer_owner) + ')' + '\n' + a_sep + '\n' + answer_text
                                answer = '\t'.join(('\n' + answer.lstrip()).splitlines(True))

                            else:
                                if answer_owner == call.from_user.id:
                                    answer = a_sep+ '\nSent by: You - ' + status + '\n' + a_sep + '\n' + answer_text
                                else:
                                    answer = a_sep + '\nSent by: #' + str(answer_owner) + ' - ' + status + '\n' + a_sep + '\n' + answer_text
                                answer = '\t'.join(('\n' + answer.lstrip()).splitlines(True))

                            f.write(answer + '\n\n')

                        f.write('\n')
                f.write(q_sep + '\n' + q_sep + '\n' + 'END OF FILE')

            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=None)
            bot.send_document(call.from_user.id, open(FILE_NAME, "r"))

        # SHOW MORE KEY
        elif call.data == 'show_more':
            bot.answer_callback_query(callback_query_id=call.id, text="Show More...")
            # SHOW MORE for a QUESTION
            if question_res is not None:
                question, keyboard = send_question(forwarded_question, call.from_user.id, short=False)
                bot.edit_message_text(question, call.from_user.id, call.message.message_id, reply_markup=keyboard)

            # SHOW MORE for an ANSWER
            elif answer_res is not None:
                answer, keyboard = send_answer(forwarded_question, forwarded_user, call.from_user.id, short=False)
                bot.edit_message_text(answer, call.from_user.id, call.message.message_id, reply_markup=keyboard)

        # SHOW LESS KEY
        elif call.data == 'show_less':
            bot.answer_callback_query(callback_query_id=call.id, text="Show Less...")
            if question_res is not None:
                question, keyboard = send_question(forwarded_question, call.from_user.id, short=True)
                bot.edit_message_text(question, call.from_user.id, call.message.message_id, reply_markup=keyboard)

            elif answer_res is not None:
                answer, keyboard = send_answer(forwarded_question, forwarded_user, call.from_user.id, short=True)
                bot.edit_message_text(answer, call.from_user.id, call.message.message_id, reply_markup=keyboard)

        # COMMENT

        elif call.data == 'comment_question':
            role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (call.from_user.id,)).fetchone()[0]
            question_state = cur.execute('''SELECT status FROM Questions WHERE id = (%s)''', (forwarded_question,)).fetchone()[0]

            if (question_state == 'OPEN'): # or (role in ['ADMIN', 'TA']):
                bot.answer_callback_query(callback_query_id=call.id, text="Send Comment!")
                cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''', ('Send Comment', call.from_user.id))
                bot.reply_to(call.message, emoji.emojize(
                    ':right_arrow: Send your Comment for: *Question ' + str(forwarded_question) + '*'),
                             reply_markup=Finish_Discard_keyboard, parse_mode='Markdown')
            else:
                # QUESTION IS CLOSED OR REPORTED
                bot.answer_callback_query(callback_query_id=call.id, text="Question is {0}!".format(question_state),
                                          show_alert=True)

        elif call.data == 'like_question':

            check_like = cur.execute('''SELECT question_id FROM Like_Question WHERE question_id = (%s) AND liked_by = (%s)''', (question_id, call.from_user.id, )).fetchone()

            if check_like is None:
                cur.execute('''INSERT INTO Like_Question (question_id, liked_by) VALUES (%s, %s)''', (question_id, call.from_user.id))
                like_number = cur.execute('''SELECT count(*) FROM Like_Question WHERE question_id = (%s)''', (question_id,)).fetchone()[0]

                if like_number % 5 == 0:
                    question_owner = cur.execute('''SELECT tel_id FROM Questions WHERE id = (%s)''', (question_id, )).fetchone()[0]
                    bot.send_message(question_owner, emoji.emojize(':red_heart: Good Job! Your Question (#Q_{0}) liked by {1} people!\n'
                                                     ':right_arrow: Keep sending smart questions.'.format(question_id, like_number)))

            bot.answer_callback_query(callback_query_id=call.id,
                                      text=emoji.emojize(":red_heart: You liked Question {0}".format(question_id)))
            try:
                keyboard = send_question(question_id, call.from_user.id, short=True)[1]
                bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard)
            except:
                pass


        # LOADING ATTACHMENTS
        ## LOADING PHOTO
        elif call.data == 'photo':
            bot.answer_callback_query(callback_query_id=call.id, text="Loading Photo...")
            if question_res is not None:
                photo_id = cur.execute('''SELECT photo FROM Questions WHERE id = (%s)''', (forwarded_question, )).fetchone()[0]
                bot.send_photo(call.from_user.id, photo_id, emoji.emojize(':framed_picture: #Q_{0}'.format(forwarded_question)), call.message.message_id)
            elif answer_res is not None:
                photo_id = cur.execute('''SELECT photo FROM Answers WHERE question_id = (%s) AND tel_id = (%s)''', (forwarded_question, forwarded_user)).fetchone()[0]
                bot.send_photo(call.from_user.id, photo_id, emoji.emojize(':framed_picture: #A_{0} #{1}'.format(forwarded_question, forwarded_user)), call.message.message_id)

        ## LOADING DOCUMENT
        elif call.data == 'document':
            bot.answer_callback_query(callback_query_id=call.id, text="Loading Document...")
            if question_res is not None:
                document_id = cur.execute('''SELECT document FROM Questions WHERE id = (%s)''', (forwarded_question, )).fetchone()[0]
                bot.send_document(call.from_user.id, document_id, call.message.message_id, caption=emoji.emojize(':paperclip: #Q_{0}'.format(forwarded_question)))
            elif answer_res is not None:
                document_id = cur.execute('''SELECT document FROM Answers WHERE question_id = (%s) AND tel_id = (%s)''', (forwarded_question, forwarded_user)).fetchone()[0]
                bot.send_document(call.from_user.id, document_id, call.message.message_id, caption=emoji.emojize(':paperclip: #A_{0} #{1}'.format(forwarded_question, forwarded_user)))

        # REPORTING A USER
        ###### COMPLETE HERE
        elif call.data == "report_user":
            role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (forwarded_user,)).fetchone()[0]

            # ONLY STUDENTS CAN BE REPORTED NOT ADMINs AND TAs
            if role == 'STUDENT':
                check_reported = cur.execute('''SELECT tel_id FROM Report_User WHERE tel_id = (%s) AND reported_by = (%s)''',
                                             (forwarded_user, call.from_user.id)).fetchone()

                if check_reported is None:

                    bot.answer_callback_query(callback_query_id=call.id, text="User Reported. Thanks!", show_alert=True)
                    cur.execute('''INSERT INTO Report_User (tel_id, reported_by) VALUES (%s, %s)''',
                                (forwarded_user, call.from_user.id))

                    ban_user_id = cur.execute(
                        '''SELECT tel_id, count(tel_id) FROM Report_User WHERE tel_id = (%s) GROUP BY tel_id HAVING count(tel_id) > (%s)''',
                        (forwarded_user, report_user_limit)).fetchone()[0]

                    if call.message.date is not None:
                        date = call.message.date
                    else:
                        date = call.message.edit_date

                    cur.execute('''UPDATE Report_User SET report_date = (%s) WHERE tel_id = (%s)''',
                                (date, ban_user_id))
                    cur.execute('''UPDATE Users SET state = 'BANNED' WHERE tel_id = (%s)''',
                                (ban_user_id, ))

                else:
                    bot.answer_callback_query(callback_query_id=call.id, text="This user has already been reported by you!", show_alert=True)

            elif role in ['ADMIN', 'TA']:
                bot.answer_callback_query(callback_query_id=call.id, text="You CANNOT report Admins and TAs!", show_alert=True)

        ##################################
        #########   QUESTION   ###########
        ##################################
        elif call.data == "follow_question":

            try:
                question_owner = cur.execute('''SELECT tel_id FROM Questions WHERE id = (%s)''', (forwarded_question, )).fetchone()[0]
                role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (question_owner, )).fetchone()[0]
                print(role)
                if role in vip:
                    bot.answer_callback_query(callback_query_id=call.id, text=emoji.emojize(
                        ":cross_mark: Cannot follow Questions sent by ADMINs or TAs."), show_alert=True)

                else:
                    if question_owner == call.from_user.id:
                        bot.answer_callback_query(callback_query_id=call.id, text=emoji.emojize(":cross_mark: Question {0} is your own question.".format(question_id)))
                    else:
                        cur.execute('''INSERT INTO Follow_Question (question_id, follower) VALUES (%s, %s)''', (forwarded_question, call.from_user.id))

                        previous_answers_num = cur.execute('''SELECT count(question_id) FROM Answers WHERE question_id = (%s)''', (forwarded_question, )).fetchone()[0]
                        bot.answer_callback_query(callback_query_id=call.id, text=emoji.emojize(":TOP_arrow: Fowlloing Question {0}"
                                                 "\n:right_arrow: Already " + str(previous_answers_num) +
                                                 " Answer(s) available in archive.".format(question_id)), show_alert=True)
            except Exception as e:
                bot.answer_callback_query(callback_query_id=call.id, text=emoji.emojize(":right_arrow: You have already followed Question " + str(forwarded_question)), show_alert= True)

        # ANSWERING A QUESTION
        elif call.data == "answer_question":
            role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (call.from_user.id, )).fetchone()[0]
            question_state = cur.execute('''SELECT status FROM Questions WHERE id = (%s)''', (forwarded_question, )).fetchone()[0]
            if (question_state == 'OPEN') or (role in ['ADMIN', 'TA']):
                bot.answer_callback_query(callback_query_id=call.id, text="Send answer!")
                cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''', ('Send Answer', call.from_user.id))
                bot.reply_to(call.message, emoji.emojize(':right_arrow: Send your answer for: *Question ' + str(forwarded_question) + '*'), reply_markup= Finish_Discard_keyboard, parse_mode='Markdown')
            else:
                # QUESTION IS CLOSED OR REPORTED
                bot.answer_callback_query(callback_query_id=call.id, text="Question is {0}!".format(question_state), show_alert=True)

        # REPORTING A QUESTION
        elif call.data == "report_question":
            # to avoid reporting a question two times from the same user
            check_reported = cur.execute('''SELECT question_id FROM Report_Question WHERE question_id = (%s) AND reported_by = (%s)''', (forwarded_question, call.from_user.id)).fetchone()

            if check_reported is None:
                bot.answer_callback_query(callback_query_id=call.id, text="Questions {0} reported. Thanks.".format(question_id), show_alert=True)
                cur.execute('''INSERT INTO Report_Question (question_id, reported_by) VALUES (%s, %s)''', (forwarded_question, call.from_user.id))



                # Questions beyond report limit will be changed to ___Reported Question___
                question_reported = cur.execute('''SELECT count(question_id) FROM Report_Question WHERE question_id = (%s)''',
                    (forwarded_question, )).fetchone()[0]

                role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (call.from_user.id, )).fetchone()[0]

                if (question_reported >= report_question_limit) or (role in instant_report_roles):
                    if role in instant_report_roles:
                        question_owner_id = cur.execute('''SELECT tel_id FROM Questions WHERE id = (%s)''', (question_id, )).fetchone()[0]
                        first_name, last_name, username = cur.execute('''SELECT first_name, last_name, username FROM Users WHERE tel_id = (%s)''', (question_owner_id, )).fetchone()

                        bot.send_message(call.from_user.id, emoji.emojize(':white_heavy_check_mark: Question #Q_{} of user: {} {} (@{}) reported.'.format(question_id, first_name, last_name, username)))
                        bot.send_message(question_owner_id, emoji.emojize(':warning: Your question #Q_{} has been reported. Please be careful when asking questions.'.format(question_id)))

                    reported_text, reported_photo, reported_document, reported_document_type, reported_document_size = \
                        cur.execute('''SELECT question, photo, document, document_type, document_size FROM Questions WHERE id = (%s)''',
                                                (forwarded_question,)).fetchone()
                    cur.execute('''UPDATE Report_Question SET reported_text = (%s), photo = (%s), document = (%s), document_type = (%s), document_size = (%s) WHERE question_id = (%s)''',
                                (reported_text, reported_photo, reported_document, reported_document_type, reported_document_size, forwarded_question,))

                    cur.execute('''UPDATE Questions SET question = (%s), status = (%s), photo = NULL, document = NULL, document_type = NULL, document_size = NULL WHERE id = (%s)''',
                                ("___Reported Question___", 'REPORTED', question_id))


            else:
                bot.answer_callback_query(callback_query_id=call.id, text="Question {0} has already been reported by you!".format(question_id),
                                          show_alert=True)

        ##################################
        #########    ANSWER    ###########
        ##################################
        # ACCEPTING AN ANSWER
        elif call.data == "accept_answer":

            accepted_answer = cur.execute('''SELECT accepted_answer FROM Answers WHERE question_id = (%s) AND tel_id = (%s)''', (forwarded_question, forwarded_user)).fetchone()[0]
            if accepted_answer == 0:


                ## Questions sent by VIP can have more than one accepted answer
                question_owner_role = cur.execute('''SELECT role FROM Users, Questions WHERE
                                      Users.tel_id = Questions.tel_id AND Questions.id = (%s)''', (question_id, )).fetchone()[0]
                # if question is NOT sent by VIP, then previous accepted answer is removed and newer answer is replaced

                accepted_already_flag = cur.execute('''SELECT accepted_answer FROM Answers WHERE question_id = (%s)''', (forwarded_question, )).fetchone()[0]

                if question_owner_role not in vip:
                    # to check if already another answer was accepted
                    cur.execute('''UPDATE Answers SET accepted_answer = 0 WHERE question_id = (%s)''', (forwarded_question, ))


                cur.execute('''UPDATE Answers SET accepted_answer = 1 WHERE question_id = (%s) AND tel_id = (%s)''', (forwarded_question, forwarded_user))
                bot.answer_callback_query(callback_query_id=call.id, text="Answer marked as accepted!")

                bot.send_message(call.from_user.id, emoji.emojize(":right_arrow: Please rate the answer:"), reply_markup=rate_accept_answer_keyboard)
                cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''',
                            ('Rate Answer', call.from_user.id))
                cur.execute('''UPDATE Questions SET status = (%s) WHERE id = (%s)''', ('CLOSED', question_id))

                # Sending Question and Accepted Answer to all users except question owner
                send_list = cur.execute('''SELECT tel_id FROM Users WHERE tel_id != (%s)''', (call.from_user.id, )).fetchall()
                
                if accepted_already_flag != 1:
                    for user in send_list:
                        try:
                            if question_owner_role not in vip:
                                bot.send_message(user[0], emoji.emojize(':white_heavy_check_mark: #Q_{0} is answered now.'.
                                            format(forwarded_question)), reply_markup=showhere_keyboard, disable_notification=True)
                            else:
                                accepted_answers_count = cur.execute('''SELECT count(answers) FROM Answers WHERE question_id = (%s) and accepted_answer = 1''', (question_id, )).fetchone()[0]
                                bot.send_message(user[0], emoji.emojize(':white_heavy_check_mark: #Q_{0} sent by ADMIN has accepted answer ({1} Accepted Answers).'
                                                                        '\n:right_arrow: Enter Question Number ({0}) to see all answers.'.format(question_id, accepted_answers_count)), disable_notification=True)
                        except Exception as e:
                            print('Sending Accepted Answer to some users failed!', e)

            else:
                bot.answer_callback_query(callback_query_id=call.id, text="Answer already accepted!", show_alert=True)

        # SHOWING ACCEPTED ANSWER and its QUESTION to receiving users
        elif call.data == 'show_here':
            # forwarded question and forwarded user is NOT VALID here.
            pattern = ':white_heavy_check_mark: #Q_(\d+) \w+' #question_id is in (\d+)
            res = re.match(pattern, emoji.demojize(message.text))
            if res is not None:
                # Sending Question
                accepted_question_id = res.group(1)
                # Sending Answer
                answer_owner = cur.execute('''SELECT tel_id FROM Answers WHERE question_id = (%s) and accepted_answer = 1''', (accepted_question_id, )).fetchone()[0]
                answer, keyboard = send_answer(accepted_question_id, answer_owner, call.from_user.id, short=True)

                bot.delete_message(call.from_user.id, call.message.message_id)
                bot.send_message(call.from_user.id, emoji.emojize(':down_arrow: Accepted answer for #Q_{0}.'.format(accepted_question_id)))
                bot.send_message(call.from_user.id, answer, reply_markup=keyboard)

        elif call.data == 'close_question':
            question_state = cur.execute('''SELECT status FROM Questions WHERE id = (%s)''', (question_id, )).fetchone()[0]
            if question_state == 'CLOSED':
                bot.answer_callback_query(callback_query_id=call.id, text=emoji.emojize(":cross_mark: Question {0} is already closed.".format(question_id)), show_alert=True)
            elif question_state == 'OPEN':
                cur.execute('''UPDATE Questions SET status = (%s) WHERE id = (%s)''', ('CLOSED', question_id))
                question_owner = cur.execute('''SELECT tel_id FROM Questions WHERE id = (%s)''', (question_id, )).fetchone()[0]
                try:
                    bot.send_message(question_owner, emoji.emojize(':cross_mark: Your Question (#Q_{0}) is closed by ADMIN.').format(question_id))
                except:
                    print('User {0} has blocked Robot.'.format(question_owner))

                bot.answer_callback_query(callback_query_id=call.id, text=emoji.emojize(":white_heavy_check_mark: Question {0} closed successfully.".format(question_id)), show_alert=True)



        ##################################
        ###    Next and Previous Page  ###
        ##################################
        elif call.data == "next_page_question":
            bot.answer_callback_query(callback_query_id=call.id, text="Next Page")
            photo, document, document_type, document_size = \
                cur.execute('''SELECT photo, document, document_type, document_size FROM Questions WHERE id = (%s)''', (forwarded_question, )).fetchone()

            # Specifying keyboard accordingly
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)


            role = cur.execute('''SELECT role FROM Users WHERE tel_id = (%s)''', (call.from_user.id, )).fetchone()[0]

            if role == 'ADMIN':
                close_question = telebot.types.InlineKeyboardButton(emoji.emojize(':cross_mark: Close'), callback_data='close_question')
                keyboard.add(close_question, report_question, follow_question, previous_page_question)
            else:
                keyboard.add(report_question, follow_question, previous_page_question)

            if photo is not None:
                keyboard.add(photo_button)
            if document is not None:
                document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: {0} ({1})'
                                  .format(document_type, document_size)), callback_data='document')
                keyboard.add(document_button)

            # Editing Message
            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard)

        elif call.data == "previous_page_question":
            bot.answer_callback_query(callback_query_id=call.id, text="Previous Page")
            keyboard = send_question(forwarded_question, call.from_user.id, short=True)[1]

            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard)

        elif call.data == "next_page_answer":
            bot.answer_callback_query(callback_query_id=call.id, text="Next Page")
            photo, document, document_type, document_size = \
                cur.execute('''SELECT photo, document, document_type, document_size FROM Answers WHERE question_id = (%s) AND tel_id = (%s)'''
                    , (forwarded_question, forwarded_user)).fetchone()
            general_keyboard = telebot.types.InlineKeyboardMarkup()
            general_keyboard.add(report_user, previous_page_answer)

            if photo is not None:
                general_keyboard.add(photo_button)
            if document is not None:
                document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: {0} ({1})'
                                  .format(document_type, document_size)), callback_data='document')
                general_keyboard.add(document_button)

            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=general_keyboard)

        elif call.data == "previous_page_answer":
            bot.answer_callback_query(callback_query_id=call.id, text="Previous Page")
            keyboard = send_answer(forwarded_question, forwarded_user, call.from_user.id, short=True)[1]

            bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard)


        ##################################
        ###    Next and Previous Page  ###
        ##################################
        # JUST A BUTTON WHEN THE BOT STARTS
        elif call.data == "send_question":
            bot.answer_callback_query(callback_query_id=call.id, text="Send your question...")
            bot.send_message(call.from_user.id, emoji.emojize(
                ':right_arrow: Send your question, then select Finish.\n\n'
                ':paperclip: 1 File and 1 Photo are allowed as attachment.'),
                             reply_markup=Finish_Discard_keyboard)
            cur.execute('''UPDATE Users SET state = (%s) WHERE tel_id = (%s)''',
                        ('Send Question', call.from_user.id))

        elif call.data == 'next_page_contact':
            bot.answer_callback_query(callback_query_id=call.id, text="Next Page")
            bot.edit_message_text(emoji.emojize(":envelope: Contact Info:\n\n"
                            ":bust_in_silhouette: Ali Arjmand:\n        :white_small_square: @AliArjomandBigdeli\n        :black_small_square: aliabigdeli@yahoo.com\n"
                            ":bust_in_silhouette: Mohammad Hossein Amini\n        :white_small_square: @MHosseinAmini\n        :black_small_square: M.hossein.amini@gmail.com \n"
                            ":bust_in_silhouette: Parsa Asadi\n        :white_small_square: @parsa_assadi\n        :black_small_square: parsaasadi145@yahoo.com\n"
                            ":bust_in_silhouette: S. Reza Hashemi:\n        :white_small_square: @SeyedReza_110\n        :black_small_square: Sr.hashemirad@yahoo.com\n"
                            ":bust_in_silhouette: Amin Ansarian\n        :white_small_square: @MarshalAmin\n        :black_small_square: Aminansarian9223@gmail.com\n"
                            ":bust_in_silhouette: Roozbeh Bazargani\n        :white_small_square: @roozbeh711\n        :black_small_square: roozbehbazargani@yahoo.com\n"
                            ":bust_in_silhouette: Amir Hossein Zamani\n        :white_small_square: @AHZ975\n        :black_small_square: Amirhosseinzamani.7596@yahoo.com"), call.from_user.id, call.message.message_id, reply_markup=previous_page_contact)

        elif call.data == 'previous_page_contact':
            bot.answer_callback_query(callback_query_id=call.id, text="Previous Page")
            bot.edit_message_text(emoji.emojize(":envelope: Contact Info:\n\n"
                            ":bust_in_silhouette: Ali Hejazi:\n        :white_small_square: @Ali_H93\n        :black_small_square: Hejazizo@ualberta.ca\n"
                            ":bust_in_silhouette: Nima Sedghiye\n        :white_small_square:  @Nima_sedghiye\n        :black_small_square: Nima.Sedghiye@gmail.com\n"
                            ":bust_in_silhouette: Hamed Hosseini\n        :white_small_square: @HMDHosseini\n        :black_small_square: hellihdhs@gmail.com")
                                  , call.from_user.id, call.message.message_id, reply_markup=next_page_contact)
# -*- coding: UTF-8 -*-
import telebot
import emoji


####################################
####         KEYBOARDS          ####
####################################
Finish_Discard_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard= True)
finish = telebot.types.KeyboardButton(emoji.emojize(':white_heavy_check_mark: Finish'))
discard = telebot.types.KeyboardButton(emoji.emojize(':cross_mark: Discard'))
Finish_Discard_keyboard.add(finish, discard)

####################################
####     GET FILE KEYBOARD      ####
####################################
getfile_keyboard = telebot.types.InlineKeyboardMarkup()
getfile = telebot.types.InlineKeyboardButton(emoji.emojize(':page_facing_up: Get File') , callback_data='getfile')
getfile_keyboard.add(getfile)

####################################
####         CHANGE EMAIL       ####
####################################
change_stnum = telebot.types.KeyboardButton(emoji.emojize(':bust_in_silhouette: Change Student Number'),)
change_stnum_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
change_stnum_keyboard.add(change_stnum)


####################################
####         MAIN KEYBOARD      ####
####################################
main_reply_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
send_question = telebot.types.KeyboardButton(emoji.emojize(':question_mark: Send Question'))
open_questions = telebot.types.KeyboardButton(emoji.emojize(':question_mark: Open Questions'))
my_profile = telebot.types.KeyboardButton(emoji.emojize(':bust_in_silhouette: My Profile'))
all_questions = telebot.types.KeyboardButton(emoji.emojize(':page_facing_up: All Questions'))
top_students = telebot.types.KeyboardButton(emoji.emojize(':high_voltage: Top Students'))
main_reply_keyboard.add(send_question)
main_reply_keyboard.add(open_questions, all_questions)
# main_reply_keyboard.add(send_question, open_questions)
main_reply_keyboard.add(my_profile, top_students)


send_question = telebot.types.InlineKeyboardButton(emoji.emojize(":question_mark: Send Question"), callback_data='send_question')
send_question_inline = telebot.types.InlineKeyboardMarkup()
send_question_inline.add(send_question)

discard_question = telebot.types.InlineKeyboardButton(emoji.emojize(":cross_mark: Discard"), callback_data='discard_question')
discard_question_inline = telebot.types.InlineKeyboardMarkup()
discard_question_inline.add(discard_question)


showmore = telebot.types.InlineKeyboardButton(u"\u2193" , callback_data='show_more')
showless = telebot.types.InlineKeyboardButton(u"\u2191" , callback_data='show_less')

####################################
####     GET FILE KEYBOARD      ####
####################################
showkeyboard_keyboard = telebot.types.InlineKeyboardMarkup()
showkeys = telebot.types.InlineKeyboardButton(emoji.emojize(u"\u2193" + 'Show Keyboard') , callback_data='show_keyboard')
showkeyboard_keyboard.add(showkeys)

####################################
####     CONTACT KEYBOARD       ####
####################################
next_page_contact = telebot.types.InlineKeyboardMarkup()
next_page_contact_button = telebot.types.InlineKeyboardButton(u"\u00BB" + ' Next' , callback_data='next_page_contact')
next_page_contact.add(next_page_contact_button)

previous_page_contact = telebot.types.InlineKeyboardMarkup()
previous_page_contact_button = telebot.types.InlineKeyboardButton(u"\u00AB" + ' Previous' , callback_data='previous_page_contact')
previous_page_contact.add(previous_page_contact_button)


####################################
####     HELP KEYBOARD       ####
####################################
next_page_help = telebot.types.InlineKeyboardMarkup()
next_page_help_button = telebot.types.InlineKeyboardButton(u"\u00BB" + ' Next' , callback_data='next_page_help')
next_page_help.add(next_page_help_button)

previous_page_help = telebot.types.InlineKeyboardMarkup()
previous_page_help_button = telebot.types.InlineKeyboardButton(u"\u00AB" + ' Previous' , callback_data='previous_page_help')
previous_page_help.add(previous_page_help_button)

####################################
####          QUESTIONS         ####
####################################

### LONG QUESTION
question_keyboard_showmore = telebot.types.InlineKeyboardMarkup()
answer_question = telebot.types.InlineKeyboardButton(emoji.emojize(":bright_button:"), callback_data='answer_question')
next_page_question = telebot.types.InlineKeyboardButton(u"\u00BB", callback_data='next_page_question')
question_keyboard_showmore.add(showmore, answer_question, next_page_question)

#### PAGE 2
follow_question = telebot.types.InlineKeyboardButton(emoji.emojize(":TOP_arrow: Follow"), callback_data='follow_question')
previous_page_question = telebot.types.InlineKeyboardButton(emoji.emojize(":BACK_arrow:") , callback_data='previous_page_question')
report_question = telebot.types.InlineKeyboardButton(emoji.emojize(":no_entry: Report"), callback_data='report_question')

####################################
####           ANSWERS          ####
####################################
answer_keyboard = telebot.types.InlineKeyboardMarkup()
next_page_answer = telebot.types.InlineKeyboardButton(u"\u00BB" , callback_data='next_page_answer')
accept_answer = telebot.types.InlineKeyboardButton(emoji.emojize(":white_heavy_check_mark: Accept"), callback_data='accept_answer')
answer_keyboard.add(accept_answer, next_page_answer)

answer_keyboard_showmore = telebot.types.InlineKeyboardMarkup()
answer_keyboard_showmore.add(showmore, accept_answer, next_page_answer)

answer_keyboard_showless = telebot.types.InlineKeyboardMarkup()
answer_keyboard_showless.add(showless, accept_answer, next_page_answer)


select_answer_showmore = telebot.types.InlineKeyboardMarkup()
select_answer_showmore.add(showmore, accept_answer, next_page_answer)

select_answer_showless = telebot.types.InlineKeyboardMarkup()
select_answer_showless.add(showless, accept_answer, next_page_answer)



#### SCROLLING BETWEEIN ANSWERS
next_answer = telebot.types.InlineKeyboardButton('Next Answer ' + u"\u00BB" , callback_data='next_answer')
previous_answer = telebot.types.InlineKeyboardButton(u"\u00AB" + ' Previous Answer', callback_data='previous_answer')


####################################
####        ANSWERS PAGE 2      ####
####################################
answer_keyboard_2 = telebot.types.InlineKeyboardMarkup()
report_user = telebot.types.InlineKeyboardButton(emoji.emojize(":prohibited: Report User"), callback_data='report_user')
previous_page_answer = telebot.types.InlineKeyboardButton(emoji.emojize(":BACK_arrow:") , callback_data='previous_page_answer')
answer_keyboard_2.add(report_user, previous_page_answer)

####################################
####       ACCEPTED ANSWER      ####
####################################
unaccept_answer_keyboard = telebot.types.InlineKeyboardMarkup()
unaccept_answer = telebot.types.InlineKeyboardButton("Unaccept Answer", callback_data='unaccept_answer')
unaccept_answer_keyboard.add(unaccept_answer)




####################################
####         RATE ANSWER        ####
####################################
star = ':bright_button:'
rate1 = telebot.types.KeyboardButton(emoji.emojize(star))
rate2 = telebot.types.KeyboardButton(emoji.emojize(star*2))
rate3 = telebot.types.KeyboardButton(emoji.emojize(star*3))
rate4 = telebot.types.KeyboardButton(emoji.emojize(star*4))
rate5 = telebot.types.KeyboardButton(emoji.emojize(star*5))

rate_accept_answer_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
rate_accept_answer_keyboard.add(rate1,rate2, rate3)
rate_accept_answer_keyboard.add(rate4, rate5)

####################################
####  SHOW MORE AND SHOW LESS   ####
####################################
showmore_keyboard = telebot.types.InlineKeyboardMarkup()

showmore_keyboard.add(showmore)

showless_keyboard = telebot.types.InlineKeyboardMarkup()
showless_keyboard.add(showless)



####################################
####     Notification KEYBOARD  ####
####################################
showhere_keyboard = telebot.types.InlineKeyboardMarkup()
showhere = telebot.types.InlineKeyboardButton(u"\u2193" + "Show here" , callback_data='show_here')
showhere_keyboard.add(showhere)


####################################
####     PHOTO AND DOCUMENT     ####
####################################
photo_button = telebot.types.InlineKeyboardButton(emoji.emojize(':framed_picture: Image'), callback_data='photo')
document_button = telebot.types.InlineKeyboardButton(emoji.emojize(':paperclip: File'), callback_data='document')
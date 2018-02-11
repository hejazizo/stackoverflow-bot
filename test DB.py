# -*- coding: UTF-8 -*-
import pgdb

####################################
######         TEST DB      ########
####################################

# ENTER YOUR DB CONFIG

print ("Using PyGreSQL")
conn = pgdb.connect(host=hostname, user=username, password=password, database=database)
cur = conn.cursor()

#***************************************#
#******         Users             ******#
#***************************************#

cur.execute('''

CREATE TABLE IF NOT EXISTS Users(
st_num INTEGER NOT NULL UNIQUE,
tel_id INTEGER UNIQUE,
first_name TEXT,
last_name TEXT,
username TEXT UNIQUE,
role TEXT,
state TEXT,
login_date INTEGER,
point DOUBLE PRECISION,
forwarded_user INTEGER,
forwarded_question INTEGER,
cont_typing TEXT,
email TEXT UNIQUE,
photo TEXT,
document TEXT,
document_type TEXT,
document_size TEXT
);
''')


cur.execute('''

CREATE TABLE IF NOT EXISTS Users_Temp(
st_num INTEGER,
tel_id INTEGER UNIQUE,
first_name TEXT,
last_name TEXT,
username TEXT UNIQUE,
login_date INTEGER,
login_code INTEGER,
state TEXT
);
''')
####################################
####      Report Users          ####
####################################
cur.execute('''

CREATE TABLE IF NOT EXISTS Report_User(
tel_id INTEGER NOT NULL,
reported_by INTEGER NOT NULL,
report_date INTEGER,
PRIMARY KEY(tel_id, reported_by)
);
''')

#***************************************#
#******         Questions         ******#
#***************************************#
cur.execute('''

CREATE TABLE IF NOT EXISTS Questions(
id INTEGER NOT NULL UNIQUE,
tel_id INTEGER NOT NULL,
question TEXT,
status TEXT,
photo TEXT,
document TEXT,
document_type TEXT,
document_size TEXT,
send_date INTEGER
);
''')

####################################
####      Follow Question      ####
####################################
cur.execute('''

CREATE TABLE IF NOT EXISTS Follow_Question(
question_id INTEGER NOT NULL,
follower INTEGER NOT NULL,
PRIMARY KEY (question_id, follower)
);
''')

####################################
####      Report Question       ####
####################################
cur.execute('''

CREATE TABLE IF NOT EXISTS Report_Question(
question_id INTEGER NOT NULL,
reported_by INTEGER NOT NULL,
reported_text TEXT,
photo TEXT,
document TEXT,
document_type TEXT,
document_size TEXT,
PRIMARY KEY (question_id, reported_by)
);
''')

#***************************************#
#******         Answers           ******#
#***************************************#
cur.execute('''

CREATE TABLE IF NOT EXISTS Answers(
id INTEGER NOT NULL UNIQUE,
question_id INTEGER NOT NULL,
tel_id INTEGER NOT NULL,
answer TEXT,
accepted_answer INTEGER,
rate_answer INTEGER,
photo TEXT,
document TEXT,
document_type TEXT,
document_size TEXT,
send_date INTEGER,
PRIMARY KEY (question_id, tel_id)  -- to provide multiple answers to a question by a specific user --> PRIMARY KEY (question_id, tel_id, answer)
);
''')

####################################
####        Report Answer       ####
####################################
cur.execute('''

CREATE TABLE IF NOT EXISTS Report_Answer(
answer_id INTEGER NOT NULL,
reported_by INTEGER NOT NULL,
PRIMARY KEY (answer_id, reported_by)
);
''')



####################################
####        LIKE QUESTION       ####
####################################
cur.execute('''
CREATE TABLE IF NOT EXISTS Like_Question(
question_id INTEGER NOT NULL,
liked_by INTEGER NOT NULL,
PRIMARY KEY (question_id, liked_by)
);
''')



#***************************************#
print('DB CREATED SUCCESSFULLY.')
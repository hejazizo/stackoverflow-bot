from DB import cur, conn

stnums_list = [90230262, # my second account
               9123107, 9123727, 9223008, 9223062, 9223093, 9223725,
               9323002, 9323008, 9323010, 9323012, 9323013, 9323016, 9323021,
               9323022, 9323027, 9323037, 9323039, 9323043, 9323046, 9323058,
               9323072, 9323082, 9323083, 9323410, 9323428, 9323701, 9323706,
               9323717, 9423011, 9423021, 9423050, 9423090, 9423901, 9523014,
               96123164,
               9323019, 9323062, 9412045, 9423011, 9423020, 9423040, 9423045,
               9423049, 9423053, 9423054, 9423055, 9423061, 9423070, 9423087,
               9423089, 9423115, 9423118, 9523005, 9523012, 9523013, 9523017,
               9523018, 9523021, 9523053]

admins_list = [9023026, 8123020]

tas_list = []

#######################################
## TEST
# stnums_list = [90230262]
# admins_list = [9023026]

cur.execute('''DELETE FROM Users_temp''')


#######################################

for stnum in stnums_list:
    if cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (stnum, )).fetchone() is None:
        cur.execute('''INSERT INTO Users (st_num, role) VALUES (%s, %s)''', (stnum, 'STUDENT'))
        print('New User: {}'.format(stnum))
    else:
        print('User already in DB {}'.format(stnum))


for admin_stnum in admins_list:
    if cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (admin_stnum, )).fetchone() is None:
        cur.execute('''INSERT INTO Users (st_num, role) VALUES (%s, %s)''', (admin_stnum, 'ADMIN'))
        print('New User: {}'.format(admin_stnum))
    else:
        print('User already in DB: {}'.format(admin_stnum))


for ta_stnum in tas_list:
    if cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (ta_stnum, )).fetchone() is None:
        cur.execute('''INSERT INTO Users (st_num, role) VALUES (%s, %s)''', (ta_stnum, 'ADMIN'))
        print('New User: {}'.format(ta_stnum))
    else:
        print('User already in DB {}'.format(ta_stnum))


conn.commit()


from DB import cur, conn

# stnums_list = [9623022, 9623023, 9623061, 9623062, 9623063, 9623064, 9623065, 9623066, 9623067, 9623068, 9623069, 9623070, 9623072, 9623073, 9623084,
#               9623085, 9623086, 9623087, 9623089, 9623090, 9623093, 9623094, 9623096, 9623098, 9623099, 9623100, 9623101, 9623102, 9623103,
#               9623104, 9623105, 9623106, 9623107, 9623108, 9623109, 9623110, 9623111, 9623112]

# admins_list = [9023026, 90230262]

#######################################
## TEST
stnums_list = [90230262]
admins_list = [9023026]

cur.execute('''DELETE FROM Users_temp''')


#######################################

for stnum in stnums_list:
    if cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (stnum, )).fetchone() is None:
        cur.execute('''INSERT INTO Users (st_num, role) VALUES (%s, %s)''', (stnum, 'STUDENT'))
    else:
        print('User already in DB')


for admin_stnum in admins_list:
    if cur.execute('''SELECT st_num FROM Users WHERE st_num = (%s)''', (admin_stnum, )).fetchone() is None:
        cur.execute('''INSERT INTO Users (st_num, role) VALUES (%s, %s)''', (admin_stnum, 'ADMIN'))
    else:
        print('User already in DB')
conn.commit()


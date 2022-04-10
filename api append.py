import sqlite3, randomstring, os

count = 1
ex = int(input('생성 기간 : '))
number = int(input('생성 개수 : '))
os.system('cls')
while True:
    con = sqlite3.connect("API.db")
    cur = con.cursor()
    api_key = randomstring.pick(20)
    cur.execute("INSERT INTO API VALUES(?, ?, ?);", ("", str(api_key), str(ex)))
    con.commit()
    print(api_key)
    if number == count:
        os.system("PAUSE")
        break
    count = count + 1
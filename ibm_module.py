import mysql.connector

host = "185.137.235.115"
user = "root"
password = "yXsePzIMB11"
db_name = "ibm"

con = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)
discord=-1


class ibm_client:
    def __init__(self, discord):
        cur = con.cursor()
        cur.execute(f"SELECT id, money, minecraftNick FROM user WHERE discordId = {discord}")
        record = cur.fetchone()
        cur.close()
        if record is None:
            self.check = False
            return
        self.check = True
        self.id = record[0]
        self.money = record[1]
        self.nick = record[2]

    def set_money(self, money):
        cur = con.cursor()
        cur.execute(f"UPDATE user SET money = money + {money} WHERE id = {self.id}")
        cur.execute(f"UPDATE user SET money = money + {money*-1} WHERE id = 2")
        con.commit()
        cur.close()

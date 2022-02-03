from main import mysql
from datetime import datetime


class MClient:
    def __init__(self, ClientId):
        cur = mysql.connection.cursor()
        cur.execute(f"""
            SELECT id, discord_id, nick, money, card, role, ban, salesman, verification, register_date, vip, ibm
            FROM users
            WHERE id = {ClientId} or discord_Id = {ClientId}
        """)
        record = cur.fetchone()
        cur.close()
        if record is None:
            self.check = False
            return
        self.check = True
        self.id = record[0]
        self.discord_id = record[1]
        self.nick = record[2]
        self.money = record[3]
        self.card = record[4]
        self.role = record[5]
        self.ban = record[6]
        self.salesman = record[7]
        self.verification = record[8]
        self.register_date = record[9]
        self.vip = record[10]
        self.ibm = record[11]

    def set_nick(self, nick):
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE users SET nick = '{nick}' WHERE id = {self.id}")
        mysql.connection.commit()
        cur.close()

    def set_ibm(self):
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE users SET ibm = '1' WHERE id = {self.id}")
        mysql.connection.commit()
        cur.close()

    def set_money(self, money):
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE users SET money = {money} WHERE id = {self.id}")
        mysql.connection.commit()
        cur.close()


class MShop:
    def __init__(self, ShopID):
        cur = mysql.connection.cursor()
        cur.execute(f"""
            SELECT id, owner, managers, name, rating, active, register_date
            FROM shops
            WHERE id = {ShopID}
        """)
        record = cur.fetchone()
        cur.close()
        if record is None:
            self.check = False
            return
        self.check = True
        self.id = record[0]
        self.owner_id = record[1]
        self.owner_name = MClient(self.owner_id).nick
        self.managers = record[2]
        self.name = record[3]
        self.active = record[4]
        self.rating = record[5]
        self.dateRegister = record[6]


class MItem:
    def __init__(self, ItemID):
        cur = mysql.connection.cursor()
        cur.execute(f"""
            SELECT id, shop, name, description, price, amount
            FROM items
            WHERE id = {ItemID}
        """)
        cur.close()
        record = cur.fetchone()
        if record is None:
            self.check = False
            return
        self.check = True
        self.id = record[0]
        self.shop = MShop(record[1])
        self.name = record[2]
        self.description = record[3]
        self.price = record[4]
        self.amount = record[5]


class GetAll:
    def __init__(self, types):
        if types == "clients":
            cur = mysql.connection.cursor()
            cur.execute(f"""
                SELECT id, discord_id, nick, money, card, role, ban, salesman, verification, register, vip
                FROM users
            """)
            record = cur.fetchall()
            cur.close()
        elif types == "shops":
            cur = mysql.connection.cursor()
            cur.execute(f"""
                SELECT id, owner, managers, name, rating, active, register_date
                FROM shops
            """)
            record = cur.fetchall()
            cur.close()
        elif types == "items":
            cur = mysql.connection.cursor()
            cur.execute(f"""
                SELECT id, shop, name, description, price, amount
                FROM items
            """)
            record = cur.fetchall()
            cur.close()
        else:
            self.check = False
            return

        if len(record) == 0:
            self.check = False
            return
        self.check = True
        self.record = record
        self.amount = len(record)


def register(discord_Id):
    if MClient(discord_Id).check:
        return False
    cur = mysql.connection.cursor()
    cur.execute(f"""
        INSERT INTO users (discord_id, nick, money, card, role, ban, salesman, verification, register_date, vip) 
        VALUES({discord_Id}, 'Установите ник', 0, 'Обычная', 'user', 0, 0, 0, '{datetime.now().date()}', False)
    """)
    mysql.connection.commit()
    cur.close()
    return True


def verification(client_id, types=-1):
    client = MClient(client_id)
    if not client.check:
        return False
    if types != -1:
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE users SET verification = {types} WHERE id = {client.id}")
    elif client.verification == 0:
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE users SET verification = 1 WHERE id = {client.id}")
    elif client.verification == 1:
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE users SET verification = 2 WHERE id = {client.id}")
    else:
        return False
    mysql.connection.commit()
    cur.close()
    return True

import os

from flask import Flask, redirect, render_template, url_for, request
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from flask_mysqldb import MySQL

import fdb
import mysqlconfig
from config import settings
import ibm_module as ibm

app = Flask(__name__)

app.config['MYSQL_HOST'] = mysqlconfig.host
app.config['MYSQL_USER'] = mysqlconfig.user
app.config['MYSQL_PASSWORD'] = mysqlconfig.password
app.config['MYSQL_DB'] = mysqlconfig.db_name
mysql = MySQL(app)

app.secret_key = b"asdasdasd asda sd asd"
app.debug = True
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "false"

app.config["DISCORD_CLIENT_ID"] = settings['DISCORD_CLIENT_ID']
app.config["DISCORD_CLIENT_SECRET"] = settings['DISCORD_CLIENT_SECRET']
app.config["DISCORD_REDIRECT_URI"] = f"http://{settings['host']}{settings['DISCORD_REDIRECT_URI']}"
app.config["DISCORD_BOT_TOKEN"] = settings['DISCORD_BOT_TOKEN']


discord = DiscordOAuth2Session(app)


def welcome_user(users):
    dm_channel = discord.bot_request("/users/@me/channels", "POST", json={"recipient_id": users.id})
    return discord.bot_request(
        f"/channels/{dm_channel['id']}/messages", "POST", json={"content": "Авторизация на сайте - прошла успешно!"}
    )


@app.context_processor
def any_data_processor():
    log_button_text = 'Логин'
    log_button_url = '/login'
    sale_check = False
    client_check = False
    if discord.user_id is not None:
        users = discord.fetch_user()
        client = fdb.MClient(users.id)
        client_check = True
        if client.salesman == 1:
            sale_check = True
    return dict(user_check=client_check, sale_check=sale_check)


@app.route("/")
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/login/")
def login():
    return discord.create_session(modified=True)


@app.route("/logout/")
def logout():
    discord.revoke()
    return redirect(url_for(".index"))


@app.route("/callback/")
def callback():
    discord.callback()
    users = discord.fetch_user()
    welcome_user(users)
    fdb.register(users.id)
    return redirect(url_for(".me"))


@app.errorhandler(Unauthorized)
def redirect_unauthorized():
    return redirect(url_for("login"))


#@app.route("/me/3/<int:check>", methods=['POST', 'GET'])
@app.route("/me/<int:opp>", methods=['POST', 'GET'])
@app.route("/me/", methods=['GET'])
@requires_authorization
def me(opp=0):
    users = discord.fetch_user()
    client = fdb.MClient(users.id)
    ibm_client = ibm.ibm_client(users.id)
    if opp == 1 and client.ibm == 0:  # ibm привязка
        if not ibm_client.check:
            return render_template(
                "error.html",
                text="У вас нет IBM аккаунта вы можете получить его в их дискорде https://discord.gg/5DFXESFZbx")
        client.set_ibm()
        client.set_nick(ibm_client.nick)
        fdb.verification(client.id, 2)
        return redirect(url_for("me"))
    elif opp == 2:  # Майнкрафт ник
        if client.verification == 0:
            if request.method == "POST":
                nick = request.form["nick"]
                client.set_nick(nick)
                fdb.verification(client.id, 1)
                return redirect(url_for("me"))
            return render_template("set_nick.html", client=client)
        if client.verification == 1:
            text = f"{client.id}"
            ver = 1
        else:
            ver = None
            text = "Вы уже подтвердили Minecraft ник"
        return render_template("sample.html",
                               title="Подтверждение ника",
                               text=text,
                               link="/me",
                               back="Вернуться на страницу профиля",
                               ver=ver)

    elif opp == 3:  # пополнение аккаунта
        if request.method == "POST":
            balance = int(request.form["balance"])
            check = request.form["check"]
            if check == "Пополнить через IBM":
                if ibm_client.money <= balance:
                    return render_template("error.html", text=f"Ваш IBM баланс: {ibm_client.money}. А вы хотите пополнить счет на {balance}")
                client.set_money(client.money+balance)
                ibm_client.set_money(-balance)
                return redirect(url_for("me"))
            else:
                return render_template("sample.html",
                                       title="Пополнение через Minecraft",
                                       text="Что-бы пополнить баланс через манйкрафт - нужно подождать :(",
                                       link="/me",
                                       back="Вернуться на страницу профиля")
        return render_template("fill_balance.html", client=client)
    elif opp == 4:  # пополнение аккаунта
        pass
    else:
        pass
    ver_scr = "/static/images/deny.png"
    ver_info = "Ошибка"
    ver_button = ""
    if client.verification == 0:
        ver_scr = "/static/images/deny.png"
        ver_info = "Установите ваш ник"
        ver_button = "Установить Minecaft ник"
    elif client.verification == 1:
        ver_scr = "/static/images/wait.png"
        ver_info = "Ожидается подтверждение"
        ver_button = "Подтвердить Minecraft Ник"
    elif client.verification == 2:
        ver_scr = "/static/images/check.png"
        ver_info = "Ник подтвержден"
        ver_button = "0"
    return render_template(
        "profile.html",
        user=users,
        info=client,
        ver_info=ver_info,
        ver_scr=ver_scr,
        ver_button=ver_button
    )


@app.route("/myshop")
def my_shop():
    users = discord.fetch_user()
    client = fdb.MClient(users.id)
    if client.salesman == 0:
        return render_template("error.html", text="У вас нету магазина")
    return render_template("shop.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host=settings['host'])

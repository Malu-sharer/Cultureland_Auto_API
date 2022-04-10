from flask import Flask, render_template, request, session, redirect
import datetime
from datetime import timedelta
import sqlite3
from auto import charge

app = Flask(__name__)

def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True

def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        how_long = (ExpireTime - ServerTime)
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return str(round(days)) + "일 " + str(round(hours)) + "시간 " + str(round(minutes)) + "분" 
    else:
        return False

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = (ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, '%Y-%m-%d %H:%M')
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)).strftime('%Y-%m-%d %H:%M')
    return ExpireTime_STR

@app.route("/api", methods=["POST"])
def _charge():
    obj = request.get_json()
    con = sqlite3.connect("API.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM API WHERE api == ?;", (obj.get("token"),))
    api = cur.fetchone()
    con.close()
    if not api == None:
        if api[0] == "":
            con = sqlite3.connect("API.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM API WHERE api == ?;", (obj.get("token"),))
            gigan = cur.fetchone()
            cur.execute("UPDATE API SET ip = ?, expiredate = ? WHERE api == ?;", (str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)), make_expiretime(int(gigan[2])), obj.get("token")))
            con.commit()
            con.close()
        obj = request.get_json()
        con = sqlite3.connect("API.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM API WHERE api == ?;", (obj.get("token"),))
        cmdchs = cur.fetchone()
        con.close()
        if not(is_expired(cmdchs[2])):
            con = sqlite3.connect("API.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM API WHERE api == ?;", (obj.get("token"),))
            ip = cur.fetchone()
            con.close()
            if not ip == None:
                pin = obj.get("pin")
                id = obj.get("id")
                pw = obj.get("pw")
                result = charge(id, pw, pin)
                return result
            else:
                return {"result": False, "amount": 0, "reason": "아이피가 올바르지 않습니다."}
        else:
            return {"result": False, "amount": 0, "reason": "만료된 라이센스입니다."}
    else:
        return {"result": False, "amount": 0, "reason": "API키가 올바르지 않습니다."}

app.run("0.0.0.0", port=4040)

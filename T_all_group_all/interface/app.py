#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask import Flask, session, redirect, url_for, escape, request, render_template
from flaskext.mysql import MySQL
# from flask_mysqldb import MySQL
# from flask_mysqldb import MySQL
# import pymysql
import bcrypt

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345678'
app.config['MYSQL_DATABASE_DB'] = 'iot'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql.init_app(app)
# cursor = mysql.get_db().cursor()


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # cur = mysql.connection.cursor()

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,hash_password))
        conn.commit()
        
        # cur = mysql.get_db().cursor()           ## point~!!!!
        # cusr.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",(name,email,hash_password))
        
        session['name'] = name
        session['email'] = email
        return redirect(url_for("home"))


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        cur = mysql.get_db().cursor()
        # cur.execute("SELECT * FROM users WHERE email=%s",(email))
        cur.execute("SELECT * FROM users WHERE email = %s;", [email])
        user = cur.fetchone()

        print(user)
        cur.close()

        if len(user) > 0  :
            # if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                # session['name'] = user['name']
                # session['email'] = user['email']
            if bcrypt.hashpw(password, user[3].encode('utf-8')) == user[3].encode('utf-8'):
                session['name'] = user[1]
                session['email'] = user[2]
                return render_template("home.html")
            else:
                return "Error password or user not match"
        else:
            return "Error password or user not match"
    else:
        return render_template("login.html")
        
@app.route('/logout')
def logout():
    session.clear()
    return render_template("home.html")

if __name__ == "__main__":
    app.secret_key = "hahahahha"
    app.run(debug=True)
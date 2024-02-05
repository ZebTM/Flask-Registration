import csv
import sqlite3
import re

from flask import Flask, request, g, render_template, redirect, url_for, session
from collections import Counter
app = Flask(__name__)

DATABASE = '/var/www/html/flaskapp/natlpark.db'
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config.from_object(__name__)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		account = execute_query('SELECT * FROM users WHERE username = ? AND password = ?', (username, password ))

		if account:
			session['loggedin'] = True

			session['username'] = account[0]
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		firstName = request.form['firstName']
		lastName = request.form['lastName']
		email = request.form['email']

		account = execute_query('SELECT * FROM users WHERE username = (?)', (username, ))

		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email or not firstName or not email or not lastName:
			msg = 'Please fill out the form !'
		else:
			execute_query('INSERT INTO users(firstName, lastName, username, password, email) VALUES ( ?, ?, ?, ?, ? )', [ firstName, lastName, username, password, email ])
			tmp = execute_query('SELECT * FROM users WHERE username = ?', ( username, ))
			msg = str(tmp)
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('registration.html', msg = msg)


def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    con = get_db()
    cur = con.execute(query, args)
    rows = cur.fetchall()
    con.commit()
    cur.close()
    return rows

@app.route("/viewdb")
def viewdb():
    rows = execute_query("""SELECT * FROM users""")
    return '<br>'.join(str(row) for row in rows)

@app.route('/')
def hello_world():
  return 'Hello from Flask!'

@app.route('/countme/<input_str>')
def count_me(input_str):
    input_counter = Counter(input_str)
    response = []
    for letter, count in input_counter.most_common():
        response.append('"{}": {}'.format(letter, count))
    return '<br>'.join(response)

@app.route("/state/<state>")
def sortby(state):
    rows = execute_query("""SELECT * FROM natlpark WHERE state = ?""",
                         [state.title()])
    return '<br>'.join(str(row) for row in rows)

if __name__ == '__main__':
  app.run()

import csv
import sqlite3

conn = sqlite3.connect('natlpark.db')
cur = conn.cursor()
cur.execute("""DROP TABLE IF EXISTS users""")
cur.execute("""CREATE TABLE users
            (firstName text, lastName text, email text, username text, password text)""")

conn.commit()
conn.close()

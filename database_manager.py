from dataclasses import dataclass
import sqlite3 as sql

def listExtension():
    con = sql.connect("databases/data_source.db")
    cur = con.cursor()
    data = cur.execute('SELECT * FROM Users ORDER BY Users.ID DESC LIMIT 10').fetchall()
    con.close()
    return data
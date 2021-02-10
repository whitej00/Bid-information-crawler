import sqlite3

conn = sqlite3.connect("tender.db")
cur = conn.cursor()
cur.execute("select Id, Company, Category from tender")
items = cur.fetchall()
for item in items:
    print(item)

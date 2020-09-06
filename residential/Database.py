import sqlite3
import time
from sqlite3 import Error


class Database:
    def __init__(self):
        try:
            db_file = r"/Users/ravibhargava/sqlite/db/repo"
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def insert_db(self, zipcode, date):
        try:
            sql = 'INSERT INTO zipcodes(zipcode, download_date) VALUES('+str(zipcode)+','+ str(date)+')'
            self.conn.execute(sql)
            self.conn.commit()
            print("Inserted into database table")
        except Error as e:
            print(e)

    def exists_db(self, zipcode):
        try:
            cur = self.conn.cursor()
            sql = 'SELECT * FROM zipcodes where zipcode = '+str(zipcode)
            cur.execute(sql)
            rows = cur.fetchall()
            if rows:
                return True
            else:
                return False
        except Error as e:
            print(e)


# z = Database()
# z.insert_db("95030", time.time())
# print(z.exists_db("95032"))
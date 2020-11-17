# Created on September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.


import sqlite3
import time
from sqlite3 import Error


class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('/Users/ravibhargava/sqlite')
        except Error as e:
            print(e)

    def create_table(self):
        try:
            c = self.conn.cursor()
            c.execute('CREATE table zipcodes(zipcode text primary key, download_date text)')
            self.conn.commit()
            print("Created table")
        except Error as e:
            print(e)

    def exists_table(self):
        try:
            c = self.conn.cursor()
            c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='zipcodes' ''')
            self.conn.commit()
            if c.fetchone()[0] == 1:
                print("Table exists")
                return True
            else:
                print("Table does not exist")
                return False
        except Error as e:
            print(e)

    def insert(self, zipcode, date):
        try:
            sql = 'INSERT INTO zipcodes(zipcode, download_date) VALUES(' + str(zipcode) + ',' + str(date) + ')'
            self.conn.execute(sql)
            self.conn.commit()
            print('Inserted '+zipcode+" into database table")
        except Error as e:
            print(e)

    def insert_db(self, zipcode, date):
        try:
            if self.exists_table():
                if not self.exists_zipcode(zipcode):
                    self.insert(zipcode, date)
                else:
                    print(zipcode +' exists')
            else:
                self.create_table()
                self.insert(zipcode, date)
        except Error as e:
            print(e)

    def exists_zipcode(self, zipcode):
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

if __name__ == '__main__':
    z = Database()
    z.insert_db("95030", str(time.time()))
    print(z.exists_zipcode("95030"))

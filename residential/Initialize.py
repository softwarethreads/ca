# Created on September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.


import sqlite3
import time
from sqlite3 import Error

from elasticsearch import Elasticsearch
from Database import Database
from Elastic import Elastic


class Initialize:
    def __init__(self):
        self.index_name = None
        self.conn = None
        self.es = Elasticsearch()
        self.db = Database()
        self.elastic = Elastic()

    def create_db_connection(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file)
            print("Connected to database successfully")
        except Error as e:
            print(e)

    def create_db_table(self):
        create_table = """ CREATE TABLE IF NOT EXISTS zipcodes (
                                            zipcode text primary key,
                                            download_date text
                                        ); """
        if self.conn is not None:
            self.conn.execute(create_table)
        else:
            print("Error! cannot create the database connection.")
        print("Created db table")

    def create_es_connection(self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        if self.es.ping():
            print('Elasticsearch Yay Connect')
        else:
            print('Awww it could not connect!')

    def create_es_index(self, zipcode):
        created = False
        # index settings
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
        try:
            index_name = 'listings_'+str(zipcode)
            if not self.db.exists_db(zipcode):
                # Ignore 400 means to ignore "Index Already Exist" error.
                self.es.indices.create(index_name, ignore=400, body=settings)
                print('Elasticsearch created index', str(index_name))
                records = self.elastic.load_es(zipcode)
                self.db.insert_db(zipcode, time.time())
                print("Loaded ", len(records), " into Elasticsearch")
            created = True
        except Exception as ex:
            print(str(ex))
        finally:
            return created


initialize = Initialize()
initialize.create_db_connection(r"/Users/ravibhargava/sqlite/db/repo")
initialize.create_db_table()

# initialize.create_es_connection()
# zipcode = '93505'
# initialize.index_name = 'listings_' + str(zipcode)
# initialize.create_es_index(zipcode)

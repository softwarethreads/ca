# Created on September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.


import ast
import json
import pprint
import time

from elasticsearch import Elasticsearch

from Database import Database
from Ingestor import Ingestor
import logging


class Elastic:
    def __init__(self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        if self.es.ping():
            logging.info('Elasticsearch connected..')
        else:
            logging.info('Could not connect to Elasticsearch!')
        self.index_name = None
        self.ingest = Ingestor()
        self.db = Database()
        self.pp = pprint.PrettyPrinter(indent=4)
        self.default_zip = None
        self.default_house = None
        self.status = None

    def store_es_record(self, house, zipcode):
        try:
            self.index_name= 'listings_'+str(zipcode)
            self.es.index(index=self.index_name, body=house)
        except Exception as ex:
            logging.info('Error in indexing data', ex)
            logging.info(str(ex))

    def load_es(self, zipcode):
        self.index_name = 'listings_' + str(zipcode)
        objects = self.ingest.callWebservice(zipcode)
        dict = objects.json()
        total = dict['result']['total']
        listings = dict['result']['listings']
        for house in listings:
            self.store_es_record(house, zipcode)
        return total

    def process(self, search_object, original_keys, modified_keys):
        try:
            res = self.es.search(index=self.index_name, body=search_object)
            data_dict = ast.literal_eval(str(res))
            num = len(data_dict['hits']['hits'])
            listing = []
            for i in range(num):
                v = data_dict['hits']['hits'][i]['_source']
                val = json.dumps(v)
                listing.append(val)
            return listing
        except Exception as ex:
            logging.info('Error in process', ex)
            logging.info(str(ex))

    def process0(self, results):
        try:
            settings = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
            zipcode = str(results[1][0])
            if not self.db.exists_zipcode(zipcode):
                # Ignore 400 means to ignore "Index Already Exist" error.
                index_name = 'listings_'+str(zipcode)
                self.es.indices.create(index_name, ignore=400, body=settings)
                print('Elasticsearch created index', str(index_name))
                num = self.load_es(zipcode)
                print("Loaded "+str(num)+" records into Elasticsearch")
                self.db.insert_db(zipcode, time.time())
                self.status = "Downloaded listings for " + str(results[1][0])
            else:
                self.status = str(results[1][0])+" already downloaded"
            self.default_zip = zip
            self.index_name = 'listings_' + str(zip)
            status = {'status': self.status}
            data = ast.literal_eval(str(status))
            result = json.dumps(data)
            return result
        except Exception as ex:
            logging.info('Error in process0', ex)
            logging.info(str(ex))
            status= {'status':'Downloading '+str(results[1][0])+' failed'}
            data = ast.literal_eval(str(status))
            result = [json.dumps(data)]
            return result

    def process6(self, results):
        #what properties are on the market in the price range 100000 to 300000
        try:
            keywords = results[1]
            key = keywords[0]
            if key == 'price':
                if len(keywords) == 3:
                    unit_low = keywords[1]
                    unit_high = keywords[2]
                    low_factor = 0
                    high_factor = 0
                    if unit_low and unit_low.startswith( 'mil' ):
                        low_factor = 1000000
                    if unit_high and unit_high.startswith( 'mil' ):
                        high_factor = 1000000
                else:
                    low_factor = 1
                    high_factor =1

            pricerange = results[2]
            low_range = pricerange[0]
            high_range = pricerange[1]
            original_keys = ["address.street", "address.city", "address.state", "address.zip", "listPrice", "sqft", "district", "size", "yearBuilt",
                             "beds", "full"]
            modified_keys = ["street", "city", "state", "zip", "listPrice", "lotSize", "district", "size", "yearBuilt",
                             "beds", "baths"]

            search_object = {
                "_source": {
                    "includes": original_keys
                },
                "query": {
                    "bool": {
                        "must": [
                            {"match": { "address.zip": self.default_zip }}
                        ],
                        "filter": [
                            {"range": { "listPrice": {"gte": int(low_range)*low_factor,
                                                     "lte": int(high_range)*high_factor
                                                     }
                                       }
                             }
                        ]
                    }
                }
            }
            val = self.process(search_object, original_keys, modified_keys)
            return val
        except Exception as ex:
            logging.info('Error in process2', ex)
            logging.info(str(ex))

    def process1(self, results):
        # "make 57402 Ernestine Radial the default house",
        try:
            address = results[1][0][0]
            default = results[1][1][0]
            house = results[1][1][1]
            #original_keys = ["address.street", "listPrice"]
            if default == 'default' and house == 'house':
                if address:
                    self.default_house = address
                    status = {'status': 'setting default house to '+self.default_house}
                else:
                    status = {'status': 'error setting default house'}
            data = ast.literal_eval(str(status))
            result = [json.dumps(data)]
            return result
        except Exception as ex:
            logging.info('Error in process2', ex)
            logging.info(str(ex))

    def process2(self, results):
        # "what is the price of the house"
        try:
            keyword = results[1][1][0]
            original_keys = ['listPrice']
            if keyword == 'price':
                search_object = {
                    "_source": {
                        "includes": [
                            "listPrice"
                        ]
                    },
                    "query": {
                        "match_phrase": {
                            "address.street": self.default_house
                        }
                    }
                }
                val = self.process(search_object, original_keys, original_keys)
                return val
        except Exception as ex:
            logging.info('Error in process3', ex)
            logging.info(str(ex))

    def process3(self, results):
        #"how many bedrooms and bathrooms does it have",
        try:
            bedrooms = results[1][0]
            bathrooms = results[1][1]

            original_keys = ["beds", "baths.full", "baths.half"]
            if (bedrooms == 'bedrooms' or bedrooms == 'bedroom') and (bathrooms == 'baths' or bathrooms == 'bathrooms' or bathrooms == 'bathroom' or bathrooms == 'bath') :
                search_object = {
                    "_source": {
                            "includes": ["beds", "baths.full", "baths.half"]
                },
                "query": {
                            "match_phrase": {
                                "address.street": self.default_house
                        }
                }
                }
                val = self.process(search_object, original_keys, original_keys)
                return val
        except Exception as ex:
            logging.info('Error in process3', ex)
            logging.info(str(ex))

    def process4(self, results):
        #"how long has the property been on the market"
        try:
            original_keys = ["daysOnHJI"]
            search_object = {
                "_source": {
                    "includes": ["daysOnHJI"]
                },
                "query": {
                    "match_phrase": {
                        "address.street": self.default_house
                    }
                }
            }
            val = self.process(search_object, original_keys, original_keys)
            return val
        except Exception as ex:
            logging.info('Error in process5', ex)
            logging.info(str(ex))

    def process5(self, results):
        #"how much section 1 work is required",
        try:
            status = {'section_1': 5000}
            data = ast.literal_eval(str(status))
            result = [json.dumps(data)]
            return result
        except Exception as ex:
            logging.info('Error in process6', ex)
            logging.info(str(ex))

    def process7(self, results):
        #"what is the required setback from lot boundary"
        try:
            status = {'setback': '25 ft'}
            data = ast.literal_eval(str(status))
            result = [json.dumps(data)]
            return result
        except Exception as ex:
            logging.info('Error in process7', ex)
            logging.info(str(ex))

    def process8(self, results):
        #set default zip = zip
        try:
            zip = str(results[1][0])
            self.default_zip = zip
            self.index_name = 'listings_'+ str(zip)
            status = {'status': 'setting default zip to '+str(zip)}
            data = ast.literal_eval(str(status))
            result = [json.dumps(data)]
            return result
        except Exception as ex:
            logging.info('Error in process8', ex)
            logging.info(str(ex))

    def process9(self, results):
        #get default zip
        try:
            if self.default_zip:
                status = {'status': 'the default zip is '+str(self.default_zip)}
            else:
                status = {'status': 'the default zip is not set'}
            data = ast.literal_eval(str(status))
            result = [json.dumps(data)]
            return result
        except Exception as ex:
            logging.info('Error in process8', ex)
            logging.info(str(ex))

    def process11(self, results):
        try:
            zip = str(results[1][0])
            original_keys = ["address.street", "address.city", "address.state", "address.zip", "listPrice", "sqft", "district", "size",
             "yearBuilt", "beds", "full"]
            modified_keys = ["street", "city", "state", "zip", "listPrice", "lotSize", "district", "size", "yearBuilt",
                             "beds", "baths"]
            search_object = {
                "_source": {
                    "includes": original_keys
                },
                "query": {
                    "bool": {
                        "must": [
                            {"match": {
                                "address.zip": zip
                            }
                            }
                        ]
                    }
                }
            }
            val = self.process(search_object, original_keys, modified_keys)
            return val
        except Exception as ex:
            logging.info('Error in process1', ex)
            logging.info(str(ex))


    def search_all(self):
        search_object = {"query": {"match_all": {}}}
        res = self.es.search(index=self.index_name, body=search_object)
        res_json = json.dumps(res)
        return res_json

    def search_id(self, id):
        search_object = {'query': {'match': {'id': str(id)}}}
        res = self.es.search(index=self.index_name, body=search_object)
        res_json = json.dumps(res)
        return res_json

    def filterKeys(self, res, original_keys, modified_keys):
        numberOfHouses = self.wrap_extract_values(res, ['value'])[0][0]
        vals = self.wrap_extract_values(res, original_keys)
        #self.pp.pprint(vals)
        numberOfAttrs = len(original_keys)
        houses = []
        for j in range(numberOfHouses):
            oneHouse = []
            for i in range(numberOfAttrs):
                if not vals[i][j] == None:
                    elem = vals[i][j]
                    oneHouse.append(elem)
            houses.append(oneHouse)
        houses_json = []
        for house in houses:
            res = dict(zip(modified_keys, house))
            houses_json.append(res)
        return houses_json

    def wrap_extract_values(self, obj, listkey):
        allvals = []
        for k in listkey:
            val = self.extract_values(obj, k)
            allvals.append(val)
        return allvals

    def extract_values(self, obj, key):
        """Pull all values of specified key from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        results = extract(obj, arr, key)
        return results





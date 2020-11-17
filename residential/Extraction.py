# Created on September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.



import re
from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk.us_extract import Lookup as ExtractLookup
import logging

class Extraction :

    def __init__(self):
        self.vocabulary = ['zip', 'zipcode', 'address', 'lot' ,'size', 'school', 'elementary', 'middle', 'high', 'price', 'cost', 'long', 'square foot','bedroom',
                 'bath', 'bathroom', 'setback', 'offers', 'million', 'millions', 'mil', 'default', 'house']
        auth_id = "4bb0e1a6-e627-4dcc-bf61-18e8888c6997"
        auth_token = "KyWfET9otO2WvqV6c9zv"
        credentials = StaticCredentials(auth_id, auth_token)
        self.client = ClientBuilder(credentials).build_us_extract_api_client()
        self.lookup = ExtractLookup()
        self.lookup.aggressive = True
        self.lookup.addresses_have_line_breaks = False
        self.lookup.addresses_per_line = 1
        self.regex = re.compile(r"(\d{5}-\d{4}|\d{5})")
        self.onlystreet = re.compile(r"(\d+\s+[A-z]+\s+[A-z]+)")
        self.longest_first = sorted(self.vocabulary, key=len, reverse=True)
        self.p = re.compile(r'(?:{})'.format('|'.join(map(re.escape, self.longest_first))))
        logging.info("Extraction initialized...")

    def getMatchingKeyords(self, input):
        f = self.p.findall(input)
        return f

    #match exact address
    def getMatchingAddress(self, query):
        self.lookup.text = query
        result = self.client.send(self.lookup)
        list_of_addresses = []
        for address in result.addresses:
            list_of_addresses.append(address.text)
        matches = self.getMatchingKeyords(query)
        return [list_of_addresses, matches]

    #match only number and street
    def getPartialAddressMatch(self, query):
        partialaddress = re.findall(self.onlystreet, query)
        matches = self.getMatchingKeyords(query)
        return [partialaddress, matches]

    def getZipcode(self, query):
        matches= re.findall(self.regex, query)
        return matches

    def getPriceRange(self, query):
        mod = query.replace(',', '')
        numbers = re.findall('[0-9]+', mod)
        return numbers

    def processQuery(self, prediction, query):
        if prediction == 0.0:
            zip = self.getZipcode(query)
            return [prediction, zip]
        if prediction == 1.0:
            address = self.getPartialAddressMatch(query)
            return [prediction, address]
        elif prediction == 2.0:
            params = self.getPartialAddressMatch(query)
            return [prediction, params]
        elif prediction == 3.0:
            keywords = self.getMatchingKeyords(query)
            return [prediction, keywords]
        elif prediction == 4.0:
            keywords = self.getMatchingKeyords(query)
            return [prediction, keywords]
        elif prediction == 5.0:
            keywords = self.getMatchingKeyords(query)
            return [prediction, keywords]
        elif prediction == 6.0:
            pricerange = self.getPriceRange(query)
            keywords = self.getMatchingKeyords(query)
            return [prediction, keywords, pricerange]
        elif prediction == 7.0:
            keywords = self.getMatchingKeyords(query)
            return [prediction, keywords]
        elif prediction == 8.0:
            zip = self.getZipcode(query)
            return [prediction, zip]
        elif prediction == 9.0:
            return [prediction]
        else:
            return None



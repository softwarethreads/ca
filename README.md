# Created on September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.


# Conversational Assistant

Residential
===========

Prerequisites
Install
- SQLite version 3.24.0
- Elasticsearch 7.8.1
- Python 3.8

Classification.py - Classifier to recognize queries

Client.py - Client program that uses voice recognition

Client0.py - Client that passes string queries

Database.py - SQLite database to keep track of zipcodes downloaded

Elastic.py - Functions to query data downloaded in Elasticsearch

Execute.py - Driver that calls Elasticsearch query based on query classification

Extraction.py - Extract key attribute values from query

Ingestor.py - Ingest the house listings from Home Junction webservice

Initialize.py - Initialize SQLite Database, Elasticsearch.

Server2.py - Server implementation. 

To run backend type 
>python3 Server2.py

To run client type 
>python3 Client0.py 
or 
>python3 Client.py

QA - Infersent implementation.
=============================





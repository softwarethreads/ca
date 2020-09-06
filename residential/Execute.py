import json
import time

from Classification import Classification
from Elastic import Elastic
from Extraction import Extraction
from Database import Database


class Execute:
    def __init__(self):
        self.classification = Classification()
        self.extraction = Extraction()
        self.elastic = Elastic()
        self.z = Database()

    def execute(self, query):
        try:
            json_data = json.loads(query)
            prediction = self.classification.predict(json_data['query'])
            results = self.extraction.processQuery(prediction[0][0], json_data['query'])
            if results[0] == 0.0:
                status = self.elastic.process0(results)
                return status
            if results[0] == 1.0:
                houses = self.elastic.process1(results)
                return houses
            elif results[0] == 2.0:
                houses = self.elastic.process2(results)
                return houses
            elif results[0] == 3.0:
                houses = self.elastic.process3(results)
                return houses
            elif results[0] == 4.0:
                houses = self.elastic.process4(results)
                return houses
            elif results[0] == 5.0:
                houses = self.elastic.process5(results)
                return houses
            elif results[0] == 6.0:
                houses = self.elastic.process6(results)
                return houses
            elif results[0] == 7.0:
                houses = self.elastic.process7(results)
                return houses
            elif results[0] == 8.0:
                status = self.elastic.process8(results)
                return status
            elif results[0] == 9.0:
                status = self.elastic.process9(results)
                return status
            else:
                return "query type " + str(results[0]) + "not supported"
        except Exception as ex:
            print(str(ex))


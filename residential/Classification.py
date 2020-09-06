from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, Tokenizer
from pyspark.sql import SparkSession
from pyspark.sql.types import DoubleType, StructType, StructField, StringType, LongType, Row
import logging

from Extraction import Extraction


class Classification:

    def __init__(self):
        self.spark = SparkSession.builder.appName("classification").config("spark.executor.memory", "70g").config("spark.driver.memory", "50g").config("spark.memory.offHeap.enabled",True).config("spark.memory.offHeap.size","16g").getOrCreate()
        schema = StructType([StructField('id', LongType(), False), StructField('text', StringType(), False), StructField('label', DoubleType(), False)])
        training = self.spark.read.format("json").load("data/questions.json", schema=schema)
        tokenizer = Tokenizer(inputCol="text", outputCol="words")
        hashingtf = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="features")
        lr = LogisticRegression(maxIter=10, regParam=0.001)
        pipeline = Pipeline(stages=[tokenizer, hashingtf, lr])
        self.model = pipeline.fit(training)
        logging.info("Classification initialized...")

    def predict(self, question):
        try:
            row = Row("id", "text")
            data = [row(1000, question)]
            df = self.spark.createDataFrame(data)
            prediction = self.model.transform(df)
            #selected = prediction.select("id", "text", "probability", "prediction").collect()
            selected = prediction.select("prediction").collect()
            return selected
        except Exception as ex:
            print(str(ex))
            return str(ex)


# c = Classification()
# e = Extraction()
#
# query = 'What properties are in 95030'
# pred = c.predict(query)
# print(pred)
# print(e.processQuery(pred[0][0], query))
#
# query = 'What is the price of 123 Main st, los gatos, ca 95030'
# pred = c.predict(query)
# print(pred)
# print(e.processQuery(pred[0][0], query))
#
# query = 'What are the houses are on sale in 95030 in the price range 1 mil to 2 mil'
# pred = c.predict(query)
# print(pred)
# print(e.processQuery(pred[0][0], query))
#

# print(c.predict('How long has the house been on the market'))
# print(c.predict('How much section 1 work does the house have'))
# print(c.predict('What is the elementary, middle and high school'))
# print(c.predict('When are they reviewing offers'))
# print(c.predict('What is the square footage of the house'))
# print(c.predict('How many bedrooms and baths does it have'))
# print(c.predict('What properties having 3 or more bedrooms are on the market in 95030'))
# print(c.predict('What is the lot size'))
# print(c.predict('How much setback can I leave if I remodel to increase square footage'))

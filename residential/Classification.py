# Created on September 6, 2020
# Copyright (c) 2020 - Software Threads, Inc.


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



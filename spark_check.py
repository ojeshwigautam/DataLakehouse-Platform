from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[1]").appName("Spark Test").getOrCreate()

print("Spark started successfully!")

print(spark.range(10).count())

spark.stop()

print("Spark stopped successfully!")

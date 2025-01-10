from pyspark.pandas import DataFrame
from pyspark.sql.connect.session import SparkSession
from pyspark.sql.types import StructType


def get_spark_df(spark: SparkSession, data: list, schema: StructType) -> DataFrame:
    return spark.createDataFrame(spark.sparkContext.parallelize(data), schema)

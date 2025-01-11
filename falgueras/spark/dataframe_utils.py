from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


def get_spark_df(spark: SparkSession, data: list, schema: StructType) -> DataFrame:
    return spark.createDataFrame(spark.sparkContext.parallelize(data), schema)

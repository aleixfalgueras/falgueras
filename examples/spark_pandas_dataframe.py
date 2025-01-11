import findspark
import pandas as pd
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType

from falgueras.common import datetime_utils
from falgueras.spark import dataframe_utils
from falgueras.spark.spark_session_utils import SparkSessionUtils

""" Spark DataFrame and Pandas DataFrame creation and conversion example """

# Spark DataFrame creation

findspark.init()
spark = SparkSessionUtils.get_spark_session("Spark Pandas DataFrame")

schema_spark_df = StructType([
    StructField("name", StringType(), True),
    StructField("surname", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("birth_date", DateType(), True)
])

data_spark_df = [
    ("Maria", "Filomena", 50, datetime_utils.get_date("2022-02-02")),
    ("Pepito", "Meloso", 80, datetime_utils.get_date("2023-03-03"))
]

spark_df = dataframe_utils.get_spark_df(spark, data_spark_df, schema_spark_df)
spark_df.show()

# Pandas DataFrame creation (data_pandas_df_json == data_pandas_df_dict)

data_pandas_df_json = [
    {"name": "Maria", "surname": "Filomena", "age": 50, "birth_date": datetime_utils.get_date("2022-02-02")},
    {"name": "Pepito", "surname": "Meloso", "age": 80, "birth_date": datetime_utils.get_date("2023-03-03")}
]
data_pandas_df_dict = {
    'name': ['Maria', 'Pepito'],
    'surname': ['Filomena', 'Meloso'],
    'age': [50, 80],
    'birth_date': [datetime_utils.get_date("2022-02-02"), datetime_utils.get_date("2023-03-03")]
}

# use astype to enforce schema
pandas_df = pd.DataFrame(data_pandas_df_json).astype({
    "name": "string",
    "surname": "string",
    "age": "int64",
    "birth_date": "datetime64[ns]"
})

print(pandas_df)

# Spark ⟺ Pandas

# from Spark to Pandas
pandas_df_from_spark_df = spark_df.toPandas()
print(pandas_df_from_spark_df)

# from Pandas to Spark
spark_df_from_pandas_df = spark.createDataFrame(pandas_df)
spark_df_from_pandas_df.show()
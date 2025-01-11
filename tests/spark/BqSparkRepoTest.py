import findspark
from pyspark.sql.types import StructField, StructType, StringType, DateType, IntegerType

from falgueras.common import datetime_utils
from falgueras.spark.dataframe_utils import get_spark_df
from falgueras.spark.repo.spark_repo import BqSparkRepo, SaveMode
from falgueras.spark.spark_session_utils import SparkSessionUtils

findspark.init()

spark = SparkSessionUtils.get_spark_session("BqSparkRepo write_partition_date test")

gcsTmpBucket = "gs://tmp-bucket-rookieml"

spark_repo_read = BqSparkRepo(spark, "rookieml.twitter.tweets_analyzed")

students_daily_repo = BqSparkRepo(spark, "rookieml.testing.students_daily", gcsTmpBucket)
students_date_partition_field = "birth_date"
studentsDateSchema = StructType([
    StructField("name", StringType(), True),
    StructField("surname", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("birth_date", DateType(), True)
])

multipleStudentsDatePartition = get_spark_df(spark, [
    ("Maria", "Filomena", 50, datetime_utils.get_date("2022-02-02")),
    ("Pepito", "Meloso", 80, datetime_utils.get_date("2023-03-03"))
], studentsDateSchema)

oneStudentDatePartition = get_spark_df(spark, [
    ("Pep", "Melós", 20, datetime_utils.get_date("2021-01-01"))
], studentsDateSchema)

oneStudentDailyDatePartition = "20210101"

students_daily_repo.write_partition_date(
    multipleStudentsDatePartition,
    SaveMode.OVERWRITE,
    students_date_partition_field
)

students_daily_repo.write_partition_date(
    oneStudentDatePartition,
    SaveMode.OVERWRITE,
    students_date_partition_field,
    date_partition=oneStudentDailyDatePartition
)

students_daily_repo.write_partition_date(
    oneStudentDatePartition,
    SaveMode.APPEND,
    students_date_partition_field,
    date_partition=oneStudentDailyDatePartition
)

students_daily_repo.read_partitions_info().show()

from abc import ABC, abstractmethod
from datetime import datetime, date
from enum import Enum
from typing import Protocol, Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from falgueras.common.datetime_utils import bq_timestamp_format
from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


class SaveMode(Enum):
    APPEND = "append"
    OVERWRITE = "overwrite"


class PartitionType(Enum):
    HOUR = "HOUR"
    DAY = "DAY"
    MONTH = "MONTH"
    YEAR = "YEAR"


class SparkRepoProtocol(Protocol):
    """Protocol to standardize Spark read and write methods for various data sources."""

    def read(self) -> DataFrame:
        """Read data and return a Spark DataFrame."""
        ...

    def write(self, data: DataFrame, save_mode: SaveMode) -> None:
        """Write a Spark DataFrame with the given SaveMode."""
        ...


class SparkRepo(ABC):
    """Abstract base class to standardize Spark read and write methods for various data sources."""

    @abstractmethod
    def read(self) -> DataFrame:
        """Abstract method to read data into a Spark DataFrame."""
        raise NotImplementedError

    @abstractmethod
    def write(self, data: DataFrame, save_mode: SaveMode) -> None:
        """Abstract method to write a Spark Dataset with the given SaveMode."""
        raise NotImplementedError


class AvroSparkRepo(SparkRepo):
    """Concrete implementation of SparkRepo for reading and writing AVRO files."""

    def __init__(self, spark: SparkSession, path: str):
        """
        Initialize the AvroRepo with the path to the AVRO file and a Spark session.

        Args:
            path (str): Path to the AVRO file or directory.
            spark (SparkSession): Active Spark session.
        """
        self.path = path
        self.spark = spark

    def read(self) -> DataFrame:
        """Reads data from the specified AVRO path into a Spark DataFrame."""

        logger.info(f"Reading AVRO from {self.path}...")
        return self.spark.read.format("avro").load(self.path)

    def write(self, data: DataFrame, save_mode: SaveMode) -> None:
        """Writes a Spark DataFrame to the specified AVRO path."""

        data.write.format("avro").mode(save_mode.value).save(self.path)
        logger.info(f"AVRO write performed at {self.path} (no guarantee of success).")


class CsvSparkRepo(SparkRepo):
    """Concrete implementation of SparkRepo for reading and writing CSV files."""

    default_options = {
        "sep": ",",
        "header": "true",
        "inferSchema": "false",
        "dateFormat": "yyyy-MM-dd",
        "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]",
        "encoding": "UTF-8",
    }

    def __init__(self,
                 spark: SparkSession,
                 path: str,
                 schema: Optional[StructType] = None,
                 read_options: Optional[dict[str, str]] = None,
                 write_options: Optional[dict[str, str]] = None):
        """
        Initialize the CsvRepo.

        Args:
            path (str): Path to the CSV file or directory.
            spark (SparkSession): Active Spark session.
            schema (StructType, optional): Optional schema for reading the CSV.
            read_options (dict, optional): Options for reading the CSV.
            write_options (dict, optional): Options for writing the CSV.
        """
        self.path = path
        self.spark = spark
        self.schema = schema
        self.read_options = read_options or CsvSparkRepo.default_options
        self.write_options = write_options or CsvSparkRepo.default_options

    def read(self) -> DataFrame:
        """Reads a CSV file into a Spark DataFrame."""

        logger.info(f"Reading CSV from {self.path}... (schema: {self.schema is not None})")

        if self.schema:
            return self.spark.read.schema(self.schema).options(**self.read_options).csv(self.path)
        else:
            return self.spark.read.options(**self.read_options).csv(self.path)

    def write(self, data: DataFrame, save_mode: SaveMode) -> None:
        """Writes a Spark DataFrame to a CSV file."""

        data.write.options(**self.write_options).mode(save_mode.value).csv(self.path)
        logger.info(f"CSV write performed at {self.path} (no guarantee of success).")


class ParquetSparkRepo(SparkRepo):
    """Concrete implementation of SparkRepo for reading and writing Parquet files."""

    def __init__(self, spark: SparkSession, path: str):
        """
        Initialize the ParquetRepo.

        Args:
            path (str): Path to the Parquet file or directory.
            spark (SparkSession): Active Spark session.
        """
        self.path = path
        self.spark = spark

    def read(self) -> DataFrame:
        """Reads a Parquet file into a Spark DataFrame."""

        logger.info(f"Reading Parquet from {self.path}...")
        return self.spark.read.parquet(self.path)

    def write(self, data: DataFrame, save_mode: SaveMode) -> None:
        """Writes a Spark DataFrame to a Parquet file."""

        data.write.mode(save_mode.value).parquet(self.path)
        logger.info(f"Parquet write performed at {self.path} (no guarantee of success).")


class BqSparkRepo(SparkRepo):
    """Concrete implementation of SparkRepo for BigQuery operations."""

    ONLY_READ_REPO = "ONLY_READ_REPO"

    def __init__(self, spark: SparkSession, table_name: str, gcs_tmp_bucket: str = ONLY_READ_REPO):
        """
        Initialize the BqRepo.

        Args:
            table_name (str): The BigQuery table name.
            spark (SparkSession): The active Spark session.
            gcs_tmp_bucket (str): Temporary GCS bucket for intermediate operations.
        """
        self.table_name = table_name
        self.spark = spark
        self.gcs_tmp_bucket = gcs_tmp_bucket

    def read(self) -> DataFrame:
        """Reads data from the BigQuery table."""
        logger.info(f"Reading {self.table_name} from BigQuery...")

        return self.spark.read.format("bigquery").load(self.table_name)

    def read_external_table(self) -> DataFrame:
        """Reads data from an external BigQuery table."""
        materialization_dataset = self.table_name.split(".")[1]
        self.spark.conf.set("materializationDataset", materialization_dataset)
        query = f"SELECT * FROM `{self.table_name}`"

        logger.info(f"Reading from external table {self.table_name} with query: \n{query}")
        return self.run_sql_query(query)

    def read_by_partitiontime_interval(self, start_datetime: datetime, end_datetime: datetime) -> DataFrame:
        """Reads partitions within a specified time interval."""
        start_formatted = bq_timestamp_format(start_datetime)
        end_formatted = bq_timestamp_format(end_datetime)
        query = f"""
            SELECT *, _PARTITIONTIME AS PARTITIONTIME
            FROM `{self.table_name}`
            WHERE _PARTITIONTIME BETWEEN TIMESTAMP('{start_formatted}') AND TIMESTAMP('{end_formatted}')
        """

        logger.info(f"Reading partitions from {start_formatted} to {end_formatted}...")
        return self.run_sql_query(query)

    def read_by_partitiontime(self, _partitiontime: datetime) -> DataFrame:
        """Reads data for a specific partition."""
        partition_hour = _partitiontime.replace(minute=0, second=0, microsecond=0)
        partition_formatted = bq_timestamp_format(partition_hour)
        query = f"""
            SELECT *, _PARTITIONTIME AS PARTITIONTIME
            FROM `{self.table_name}`
            WHERE _PARTITIONTIME = TIMESTAMP('{partition_formatted}')
        """

        logger.info(f"Reading partition for time {partition_formatted}...")
        return self.run_sql_query(query)

    def read_by_partitiondate(self, _partitiondate: date):
        """_PARTITIONDATE value is equal to _PARTITIONTIME truncated to date."""
        self.read_by_partitiontime(datetime.combine(_partitiondate, datetime.min.time()))

    def read_by_partitiondate_interval(self, start_date: date, end_date: date):
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time())
        self.read_by_partitiontime_interval(start_datetime, end_datetime)
    def write(self, data: DataFrame, save_mode: SaveMode) -> None:
        """Writes data to the BigQuery table."""
        logger.info(f"Writing to BigQuery table {self.table_name}...")

        (data
         .write
         .format("bigquery")
         .mode(save_mode.value)
         .option("writeMethod", "direct")
         .save(self.table_name))

        logger.info("Success writing")

    def write_in_ingestion_partitioned_table(self, data: DataFrame, save_mode: SaveMode) -> None:
        """At today, Direct write method does not support writing to a partitioned ingestion table."""
        logger.info(f"Writing to partitioned BigQuery table {self.table_name}...")

        (data
         .write
         .format("bigquery")
         .mode(save_mode.value)
         .option("temporaryGcsBucket", self.gcs_tmp_bucket)
         .save(self.table_name))

    def write_partition_date(self,
                             data: DataFrame,
                             save_mode: SaveMode,
                             partition_field: str,
                             partition_type: PartitionType = PartitionType.DAY,
                             date_partition: str = None) -> None:
        """
        Writes data to a BigQuery table partitioned by HOUR, DAY, MONTH, or YEAR.

        For daily partitioning, only options "partitionField" or "datePartition" are required (because of default values):
         partitionField + Overwrite -> Overwrite the entire table with the new partitions.
         partitionField + Append    -> Append records to the existing partitions and create new partitions if necessary.
         datePartition  + Overwrite -> Overwrite only the specified partition.
         datePartition  + Append    -> Append new records only the specified partition.

        For other partitioning strategies:
         insert multiple partitions -> partitionField + partitionType required
         insert single partition    -> datePartition + partitionField + partitionType required

        Ref: https://github.com/GoogleCloudDataproc/spark-bigquery-connector
        :param data: data to save
        :param save_mode: save mode
        :param partition_field: partitioning field of the table
        :param partition_type: partition type of the table, possible values: HOUR, DAY, MONTH, YEAR
        :param date_partition: date of the specific partition to write, valid formats: yyyyMMddHH, yyyyMMdd, yyyyMM, yyyy
        """
        options = {
            "temporaryGcsBucket": self.gcs_tmp_bucket,
            "partitionField": partition_field,
            "partitionType": partition_type.value,
        }

        if date_partition:
            options["datePartition"] = date_partition
            logger.info(f"Writing partition in BigQuery table {self.table_name}: \n" +
                        f"[partition ID = {date_partition}, partition field = {partition_field}, " +
                        f"partition type = {partition_type}, mode = {save_mode}]")
        else:
            logger.info(f"Writing partitions in BigQuery table {self.table_name}: \n" +
                        f"[partition ID = multiple inserts, partition field = {partition_field}, " +
                        f"partition type = {partition_type}, mode = {save_mode}]")

        data.write.format("bigquery").mode(save_mode.value).options(**options).save(self.table_name)
        logger.info("Success writing")

    def truncate_repo(self) -> None:
        """Truncates the BigQuery table."""
        logger.info(f"Truncating BigQuery table {self.table_name}...")
        query = f"TRUNCATE TABLE {self.table_name}"
        self.run_sql_query(query)

    def read_partitions_info(self) -> DataFrame:
        """Reads partition information for the BigQuery table."""
        project, dataset, table = self.table_name.split(".")
        query = f"""
            SELECT partition_id, total_rows, total_logical_bytes, last_modified_time
            FROM `{project}.{dataset}.INFORMATION_SCHEMA.PARTITIONS`
            WHERE table_name = '{table}'
            ORDER BY last_modified_time DESC
        """
        logger.info(f"Reading partition info for BigQuery table {self.table_name}...")
        return self.run_sql_query(query)

    def run_sql_query(self, query: str) -> DataFrame:
        """Executes a SQL query on BigQuery."""
        self.spark.conf.set("viewsEnabled", "true")
        materialization_dataset = self.table_name.split(".")[1]
        self.spark.conf.set("materializationDataset", materialization_dataset)

        logger.info(f"Running query: \n{query}")
        return self.spark.read.format("bigquery").option("query", query).load()

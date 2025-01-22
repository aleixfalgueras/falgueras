from abc import ABC, abstractmethod
from enum import Enum
from io import StringIO
from typing import Protocol

from google.cloud import bigquery
from pandas import DataFrame, read_csv

from falgueras.common.logging_utils import get_colored_logger
from falgueras.gcp.BqClient import BqClient
from falgueras.gcp.GcsClient import GcsClient

logger = get_colored_logger(__name__)


class WriteMode(Enum):
    APPEND = "APPEND"
    TRUNCATE = "TRUNCATE"
    UPDATE = "UPDATE"
    CREATE = "CREATE"
    REPLACE = "REPLACE"


class PandasRepoProtocol(Protocol):
    """
    Protocol to enforce type compliance at the function signature level.
    """

    def read(self, **kwargs) -> DataFrame:
        """Read data into a DataFrame."""
        ...

    def write(self, data: DataFrame, write_mode: WriteMode, index=False, **kwargs) -> None:
        """Write a DataFrame to a destination."""
        ...


class PandasRepo(ABC):
    """Abstract base class for reading and writing pandas DataFrames."""

    @abstractmethod
    def read(self, **kwargs) -> DataFrame:
        """Abstract method to read data into a DataFrame."""
        raise NotImplementedError

    @abstractmethod
    def write(self, data: DataFrame, write_mode: WriteMode, index=False, **kwargs) -> None:
        """Abstract method to write a DataFrame to a destination."""
        raise NotImplementedError


class BqPandasRepo(PandasRepo):
    """Concrete implementation for reading and writing DataFrames to BigQuery."""

    def __init__(self, table_name: str, bq_client: BqClient = None):
        """
        Initializes the repository with a target table and BigQuery client.

        Args:
            table_name (str): The target BigQuery table.
            bq_client (BqClient): A BigQuery client for interacting with the service.
        """
        if table_name.count('.') < 1 or table_name.count('.') > 2:
            raise ValueError(
                "The table must be in the format 'dataset_id.table_id' or 'project_id.dataset_id.table_id'."
            )
        if bq_client is None:
            bq_client = BqClient()

        self.client = bq_client
        self.table_name = table_name

    def read(self, **kwargs) -> DataFrame:
        """ Reads data from BigQuery as a Pandas DataFrame. """
        query = kwargs.get("query", "")
        where_filter = kwargs.get("where_filter", "")

        try:
            if not query and not where_filter:
                query = f"SELECT * FROM {self.table_name}"
            elif not query:
                query = f"SELECT * FROM {self.table_name} WHERE {where_filter}"

            return self.client.run_query(query).to_dataframe()

        except Exception as e:
            raise RuntimeError(f"Failed to read data from BigQuery: {e}")

    def write(self,
              data: DataFrame,
              write_mode: WriteMode,
              *, index: bool = False,
              **kwargs) -> None:
        """ Writes a Pandas DataFrame to the BigQuery table."""
        logger.info(f"Writing to {self.table_name} with WriteMode {write_mode.value}, "
                    f"extra args (if any): {kwargs}.")
        try:
            if write_mode == WriteMode.CREATE:
                self.client.load_table_from_pandas_df(
                    data,
                    self.table_name,
                    bigquery.WriteDisposition.WRITE_TRUNCATE
                )
            elif write_mode == WriteMode.TRUNCATE:
                self.client.load_table_from_pandas_df(
                    data,
                    self.table_name,
                    bigquery.WriteDisposition.WRITE_TRUNCATE,
                    bigquery.CreateDisposition.CREATE_NEVER
                )
            elif write_mode == WriteMode.APPEND:
                self.client.load_table_from_pandas_df(
                    data,
                    self.table_name,
                    bigquery.WriteDisposition.WRITE_APPEND,
                    bigquery.CreateDisposition.CREATE_NEVER
                )
            elif write_mode == WriteMode.UPDATE:
                temporal_table_name = self.table_name + "_temp"
                update_key = kwargs.get("update_key", "id")  # column name which acts as a join key
                columns_to_update = kwargs.get("columns_to_update", "")
                # a list with the table column names following the table schema definition order

                try:
                    self.client.load_table_from_pandas_df(
                        data,
                        temporal_table_name,
                        bigquery.WriteDisposition.WRITE_TRUNCATE
                    )

                    columns_to_update = ", ".join([f"{column_name} = source.{column_name}"
                                                   for column_name in columns_to_update])
                    update_query = f"""
                        MERGE {self.table_name} AS target
                        USING {temporal_table_name} AS source
                        ON target.{update_key} = source.{update_key}
                        WHEN MATCHED THEN
                          UPDATE SET
                            {columns_to_update}   
                        """

                    self.client.run_query(update_query)
                    self.client.run_query(f"DROP TABLE IF EXISTS {temporal_table_name}")
                except Exception as exc:
                    self.client.run_query(f"DROP TABLE IF EXISTS {temporal_table_name}")
                    raise exc
            elif write_mode == WriteMode.REPLACE:
                replace_condition = kwargs.get("replace_condition", None)
                self.delete(replace_condition)

                self.client.load_table_from_pandas_df(
                    data,
                    self.table_name,
                    bigquery.WriteDisposition.WRITE_APPEND,
                    bigquery.CreateDisposition.CREATE_NEVER
                )
            else:
                raise ValueError(
                    f"Unsupported write_mode: {write_mode}, "
                    f"available: {[e.value for e in WriteMode]}"
                )
        except Exception as e:
            raise RuntimeError(f"Failed to write data to BigQuery table {self.table_name} "
                               f"with write mode {write_mode}: {e}")

    def delete(self, where_filter):
        self.run_query(f"DELETE from {self.table_name} WHERE {where_filter}")

    def truncate_table(self):
        self.run_query(f"TRUNCATE TABLE {self.table_name}")

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
        return self.client.run_query(query).to_dataframe()

    def run_query(self, query) -> None: self.client.run_query(query)


class GcsPandasRepo(PandasRepo):
    """Concrete implementation for reading and writing DataFrames to GCS."""

    def __init__(self,
                 path: str,
                 bucket: str,
                 gcs_client: GcsClient,
                 *, content_type: str = "text/csv"):
        """
        Initialize the GCS repository.

        Args:
            bucket (str): GCS bucket name.
            path (str): Path within the GCS bucket.
            gcs_client (GcsClient): Custom class to handle Google Cloud Storage (GCS) operations.
            content_type (str): MIME type for the file. Defaults to "text/csv".
        """
        self.path = path
        self.bucket = bucket
        self.gcs = gcs_client
        self.content_type = content_type

    def read(self) -> DataFrame:
        """Read a CSV file from GCS into a DataFrame."""
        try:
            csv_data = self.gcs.read_text(self.bucket, self.path)
            return read_csv(StringIO(csv_data))
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV from GCS path {self.path} in bucket {self.bucket}: {e}")

    def write(self, data: DataFrame, write_mode: WriteMode, *, index: bool = False, **kwargs) -> None:
        """Write a DataFrame to a CSV file in GCS."""
        try:
            csv_buffer = StringIO()
            data.to_csv(csv_buffer, index=index)
            csv_buffer.seek(0)
            self.gcs.write_string(self.bucket,
                                  self.path,
                                  csv_buffer.getvalue(),
                                  content_type=self.content_type)
        except Exception as e:
            raise RuntimeError(f"Failed to write CSV to GCS path {self.path} in bucket {self.bucket}: {e}")


class CsvPandasRepo(PandasRepo):
    """Concrete implementation for reading and writing CSV files locally."""

    def __init__(self, path: str):
        """
        Initialize the CSV repository.

        Args:
            path (str): The local file path.
        """
        self.path = path

    def read(self, **kwargs) -> DataFrame:
        """Read a CSV file into a DataFrame."""
        try:
            return read_csv(self.path, **kwargs)
        except Exception as e:
            raise RuntimeError(f"Failed to read CSV from {self.path}: {e}")

    def write(self, data: DataFrame, write_mode: WriteMode, *, index: bool = False, **kwargs) -> None:
        """Write a DataFrame to a CSV file."""
        try:
            data.to_csv(self.path, index=index)
        except Exception as e:
            raise RuntimeError(f"Failed to write CSV to {self.path}: {e}")
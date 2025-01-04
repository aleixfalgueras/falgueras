from typing import Optional

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import bigquery
from google.cloud.bigquery import WriteDisposition, CreateDisposition
from google.cloud.bigquery.table import RowIterator
from pandas import DataFrame

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


class BqClient:
    """ A class to handle BigQuery (BQ) operations. """

    BQ_DATE_FORMAT = "%Y-%m-%d"
    BQ_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"  # YYYY-MM-DDTHH:MM:SS[.FFFFFF][+/-HH:MM]

    def __init__(self, client: Optional[bigquery.Client] = None):
        """
        Initializes the BigQuery client.

        Args:
            client (Optional[bigquery.Client]): An optional instance of the BigQuery client.
                If not provided, a new client instance will be created.
        """
        self.client = bigquery.Client() if client is None else client

    def create_dataset(self, project_id: str, dataset_id: str, location: str="US"):
        """
        Creates a dataset if it doesn't exist.

        Args:
            project_id (str): The GCP project ID.
            dataset_id (str): The dataset ID.
            location (str): The dataset location.
        """
        dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
        try:
            self.client.get_dataset(dataset_ref)
            print(f"Dataset {project_id}.{dataset_id} already exists.")
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = location
            self.client.create_dataset(dataset)
            print(f"Dataset {project_id}.{dataset_id} created successfully.")

    def run_query(self, query: str) -> bigquery.table.RowIterator:
        """
        Executes a BigQuery SQL query and returns the results.

        Args:
            query (str): The SQL query to execute.

        Returns:
            RowIterator: An iterator over the query results.

        Raises:
            GoogleAPICallError: If the query execution fails.
        """
        try:
            logger.info(f"Running BQ query:\n\t{query}")
            return self.client.query(query).result()
        except GoogleAPICallError as e:
            logger.error(f"Failed to execute query:\n{query}\nException:\n{e}")
            raise RuntimeError(f"Failed to execute query: {e}")

    def load_table_from_pandas_df(self,
                                  df: DataFrame,
                                  table_name: str,
                                  write_disposition: WriteDisposition,
                                  create_disposition: CreateDisposition = CreateDisposition.CREATE_IF_NEEDED):
        """
        Loads a Pandas DataFrame into a BigQuery table.

        Args:
            df (DataFrame): The Pandas DataFrame to load into BigQuery.
            table_name (str): Fully qualified table name in the format:
                              "project_id.dataset_id.table_id" or "dataset_id.table_id" (when using default project).
            write_disposition (WriteDisposition): Specifies the behavior when writing to an existing table.
                Options include:
                    - WriteDisposition.WRITE_TRUNCATE: Overwrite the table data.
                    - WriteDisposition.WRITE_APPEND: Append to the existing table data.
                    - WriteDisposition.WRITE_EMPTY: Fails if the table is not empty.
            create_disposition (CreateDisposition): Specifies the behavior when the table does not exist.
                Defaults to CreateDisposition.CREATE_IF_NEEDED. Options include:
                    - CreateDisposition.CREATE_IF_NEEDED: Creates the table if it does not exist.
                    - CreateDisposition.CREATE_NEVER: Fails if the table does not exist.

        Raises:
            ValueError: If `table_name` does not include at least dataset and table (e.g., "dataset_id.table_id").
            google.cloud.exceptions.GoogleCloudError: If the load job fails.
        """
        # Validate table_name format
        if table_name.count('.') < 1 or table_name.count('.') > 2:
            raise ValueError(
                "The table_name must be in the format 'project_id.dataset_id.table_id' or 'dataset_id.table_id'."
            )

        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = write_disposition
        job_config.create_disposition = create_disposition

        try:
            load_job = self.client.load_table_from_dataframe(df, table_name, job_config=job_config)
            load_job.result()
            logger.info(f"Data successfully loaded into {table_name}.")
        except Exception as e:
            raise RuntimeError(f"Failed to load data into {table_name}: {e}")

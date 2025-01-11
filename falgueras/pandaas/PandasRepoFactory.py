from falgueras.pandaas.pandas_repo import *


class PandasRepoType(Enum):
    CSV = "CSV"
    GCS = "GCS"
    BQ = "BQ"

class PandasRepoFactory:
    """Factory class for creating PandasRepo objects."""

    @staticmethod
    def create(repo_type: PandasRepoType, *args, **kwargs) -> PandasRepo:
        """Factory method to create a PandasRepo object based on the type."""
        if repo_type == PandasRepoType.CSV:
            return CsvPandasRepo(*args, **kwargs)
        elif repo_type == PandasRepoType.GCS:
            return GcsPandasRepo(*args, **kwargs)
        elif repo_type == PandasRepoType.BQ:
            return BqPandasRepo(*args, **kwargs)
        else:
            raise ValueError(f"Unsupported repo type: {repo_type}, "
                             f"available: {[e.value for e in PandasRepoType]}")

    @staticmethod
    def create_bq_repo(table_name: str, bq_client: BqClient) -> BqPandasRepo:
        """
        Create a BqPandasRepo instance.

        Args:
            table_name (str): Bq table name with format project_id.dataset_id.table_id or dataset_id.table_id.
            bq_client (BqClient): An object to handle BigQuery (BQ) operations
        Returns:
            BqPandasRepo: Instance for BQ operations.
        """
        return BqPandasRepo(table_name=table_name, bq_client=bq_client)

    @staticmethod
    def create_csv_repo(path: str) -> CsvPandasRepo:
        """
        Create a CsvPandasRepo instance.

        Args:
            path (str): Path to the local CSV file.

        Returns:
            CsvPandasRepo: Instance for local CSV operations.
        """
        return CsvPandasRepo(path=path)

    @staticmethod
    def create_gcs_repo(path: str,
                        bucket: str,
                        gcs_client: GcsClient,
                        *,
                        content_type: str = "text/csv") -> GcsPandasRepo:
        """
        Create a GcsPandasRepo instance.

        Args:
            bucket (str): GCS bucket name.
            path (str): Path within the GCS bucket.
            gcs_client (GcsClient): An object to handle Google Cloud Storage (GCS) operations.
            content_type (str): MIME type for the file. Defaults to "text/csv".
        Returns:
            GcsPandasRepo: Instance for GCS operations.
        """
        return GcsPandasRepo(
            path=path,
            bucket=bucket,
            gcs_client=gcs_client,
            content_type=content_type)

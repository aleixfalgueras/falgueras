from typing import Dict

from falgueras.spark.repo.spark_repo import *


class SparkRepoType(Enum):
    BQ = "BQ"
    CSV = "CSV"
    AVRO = "AVRO"
    PARQUET = "PARQUET"


class SparkRepoFactory:
    """SparkRepo factory methods"""

    @staticmethod
    def get_gcs_spark_repo(spark_repo_type: SparkRepoType, gcs_path: str,
                           schema: Optional[StructType] = None,
                           read_options: Optional[Dict[str, str]] = None,
                           write_options: Optional[Dict[str, str]] = None,
                           spark: SparkSession = None) -> SparkRepo:
        return SparkRepoFactory.get_spark_repo(
            spark=spark,
            spark_repo_type=spark_repo_type,
            data_path=gcs_path,
            is_gcs_path=True,
            schema=schema,
            read_options=read_options,
            write_options=write_options
        )

    @staticmethod
    def get_spark_repo(
            spark: SparkSession,
            spark_repo_type: SparkRepoType,
            bq_table_name: Optional[str] = None,
            gcs_tmp_bucket: Optional[str] = None,
            schema: Optional[StructType] = None,
            read_options: Optional[Dict[str, str]] = None,
            write_options: Optional[Dict[str, str]] = None,
            data_path: Optional[str] = None,
            is_gcs_path: bool = False) -> SparkRepo:

        def get_gcs_path(gcs_path: str) -> str:
            return gcs_path if gcs_path.startswith("gs://") else f"gs://{gcs_path}"

        if spark_repo_type == SparkRepoType.BQ:
            if not bq_table_name:
                raise ValueError("bq_table_name parameter must be provided for BQ SparkRepoType.")
            if not gcs_tmp_bucket:
                return BqSparkRepo(spark=spark, table_name=bq_table_name)
            else:
                return BqSparkRepo(spark=spark, table_name=bq_table_name, gcs_tmp_bucket=gcs_tmp_bucket)
        elif spark_repo_type in {SparkRepoType.CSV, SparkRepoType.AVRO, SparkRepoType.PARQUET}:
            if not data_path:
                raise ValueError(f"data_path parameter must be provided for {spark_repo_type.name} SparkRepoType.")

            path = get_gcs_path(data_path) if is_gcs_path else data_path

            if spark_repo_type == SparkRepoType.CSV:
                return CsvSparkRepo(spark=spark,
                                    path=path,
                                    schema=schema,
                                    read_options=read_options,
                                    write_options=write_options)
            elif spark_repo_type == SparkRepoType.AVRO:
                return AvroSparkRepo(spark=spark, path=path)
            elif spark_repo_type == SparkRepoType.PARQUET:
                return ParquetSparkRepo(spark=spark, path=path)
        else:
            raise NotImplementedError(f"SparkRepo for {spark_repo_type.name} not implemented.")

import os
import unittest
from tempfile import TemporaryDirectory

import findspark
from pyspark.sql.types import StructField, StringType, IntegerType

from falgueras.spark.repo.spark_repo import *
from falgueras.spark.spark_session_utils import SparkSessionUtils

findspark.init()


class SparkRepoTest(unittest.TestCase):
    """Test CsvSparkRepo, AvroSparkRepo and ParquetSparkRepo"""

    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSessionUtils.get_spark_session("SparkRepoTest")
        cls.spark.sparkContext.setLogLevel("ERROR")

        # Create a sample DataFrame
        cls.schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
        ])
        cls.sample_data = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]
        cls.sample_df = cls.spark.createDataFrame(cls.sample_data, schema=cls.schema)

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_avro_repo(self):
        with TemporaryDirectory() as tmp_dir:
            repo_path = os.path.join(tmp_dir, "test_avro")
            avro_repo = AvroSparkRepo(repo_path, self.spark)

            # Test Write
            avro_repo.write(self.sample_df, SaveMode.OVERWRITE)
            self.assertTrue(os.path.exists(repo_path))

            # Test Read
            df = avro_repo.read()
            self.assertEqual(df.count(), len(self.sample_data))
            self.assertEqual(set(df.columns), set(self.schema.fieldNames()))

    def test_csv_repo(self):
        with TemporaryDirectory() as tmp_dir:
            repo_path = os.path.join(tmp_dir, "test_csv")
            csv_repo = CsvSparkRepo(repo_path, self.spark)

            csv_repo.write(self.sample_df, SaveMode.OVERWRITE)
            self.assertTrue(os.path.exists(repo_path))

            df = csv_repo.read()
            self.assertEqual(df.count(), len(self.sample_data))
            self.assertEqual(set(df.columns), set(self.schema.fieldNames()))

    def test_csv_repo_with_custom_options(self):
        with TemporaryDirectory() as tmp_dir:
            custom_read_options = {
                "header": "true",
                "inferSchema": "true",
                "sep": "|"
            }
            custom_write_options = {
                "header": "true",
                "sep": "|"
            }

            repo_path = os.path.join(tmp_dir, "test_csv_custom")
            csv_repo = CsvSparkRepo(
                path=repo_path,
                spark=self.spark,
                schema=self.schema,
                read_options=custom_read_options,
                write_options=custom_write_options
            )

            csv_repo.write(self.sample_df, SaveMode.OVERWRITE)
            self.assertTrue(os.path.exists(repo_path))

            df = csv_repo.read()

            # check length and schema
            self.assertEqual(df.count(), len(self.sample_data))
            self.assertEqual(set(df.columns), set(self.schema.fieldNames()))

            # check at least one CSV file is written
            written_files = [f for f in os.listdir(repo_path) if f.endswith(".csv")]
            self.assertTrue(len(written_files) > 0)

            # read the written file directly to verify content
            written_file_path = os.path.join(repo_path, written_files[0])
            with open(written_file_path, "r") as f:
                content = f.read()
            self.assertIn("id|name", content)  # validate custom separator in the header

    def test_parquet_repo(self):
        with TemporaryDirectory() as tmp_dir:
            repo_path = os.path.join(tmp_dir, "test_parquet")
            parquet_repo = ParquetSparkRepo(repo_path, self.spark)

            parquet_repo.write(self.sample_df, SaveMode.OVERWRITE)
            self.assertTrue(os.path.exists(repo_path))

            df = parquet_repo.read()
            self.assertEqual(df.count(), len(self.sample_data))
            self.assertEqual(set(df.columns), set(self.schema.fieldNames()))

if __name__ == "__main__":
    unittest.main()

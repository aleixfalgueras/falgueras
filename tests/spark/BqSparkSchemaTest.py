import os
import unittest

from google.cloud.bigquery import SchemaField
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from falgueras.spark.BqSparkSchema import BqSparkSchema


class TestBqSparkSchema(unittest.TestCase):

    def setUp(self):
        self.schema_file_path = os.path.join(os.path.dirname(__file__), "bq_schema.json")

    def test_get_spark_schema(self):
        """Test the conversion of a BigQuery JSON schema to a Spark schema."""

        expected_spark_schema = StructType([
            StructField("seller_id", StringType(), False),
            StructField("seller_name", StringType(), True),
            StructField("daily_target", IntegerType(), True),
        ])
        spark_schema = BqSparkSchema.get_spark_schema(self.schema_file_path)

        self.assertEqual(spark_schema, expected_spark_schema)

    def test_get_bq_schema(self):
        """Test the conversion of a Spark schema to a BigQuery schema."""

        input_spark_schema = StructType([
            StructField("seller_id", StringType(), False),
            StructField("seller_name", StringType(), True),
            StructField("daily_target", IntegerType(), True),
        ])
        expected_bq_schema = [
            SchemaField("seller_id", "STRING", "REQUIRED"),
            SchemaField("seller_name", "STRING", "NULLABLE"),
            SchemaField("daily_target", "INT64", "NULLABLE"),
        ]
        bq_schema = BqSparkSchema.get_bq_schema(input_spark_schema)

        self.assertEqual(bq_schema, expected_bq_schema)


if __name__ == "__main__":
    unittest.main()

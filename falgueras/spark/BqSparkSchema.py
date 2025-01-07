import json

from google.cloud.bigquery import SchemaField
from pyspark.sql.types import (
    BooleanType, StringType, IntegerType, DecimalType, DoubleType,
    DateType, TimestampType, StructField, StructType
)


class BqSparkSchema:
    """Utility class for converting between BigQuery and Spark schemas."""

    @staticmethod
    def bq_type_to_spark_type(bq_type: str):
        bq_to_spark_mapping = {
            "BOOLEAN": BooleanType(),
            "STRING": StringType(),
            "INT64": IntegerType(),
            "INT": IntegerType(),
            "SMALLINT": IntegerType(),
            "BIGINT": IntegerType(),
            "TINYINT": IntegerType(),
            "BYTEINT": IntegerType(),
            "INTEGER": IntegerType(),
            "NUMERIC": DecimalType(38, 9),
            "DECIMAL": DecimalType(38, 9),
            "BIGNUMERIC": DecimalType(38, 38),
            "BIGDECIMAL": DecimalType(38, 38),
            "FLOAT64": DoubleType(),
            "DATE": DateType(),
            "DATETIME": TimestampType(),
            "TIMESTAMP": TimestampType(),
        }

        if bq_type.upper() in bq_to_spark_mapping:
            return bq_to_spark_mapping[bq_type.upper()]
        else:
            raise Exception(f"Spark type for BigQuery type {bq_type} not known")

    @staticmethod
    def get_spark_schema(schema_path: str) -> StructType:
        """
        Converts a BigQuery JSON schema definition into a Spark StructType schema.

        Args:
            schema_path (str): Path to the JSON file with the BigQuery schema.

        Returns:
            StructType: The corresponding Spark schema.
        """
        with open(schema_path, 'r') as file:
            json_schema = json.load(file)

        fields = [
            StructField(
                field["name"],
                BqSparkSchema.bq_type_to_spark_type(field["type"]),
                field.get("mode", "NULLABLE") != "REQUIRED"
            )
            for field in json_schema
        ]

        return StructType(fields)

    @staticmethod
    def get_bq_schema(struct_type: StructType):
        """
        Converts a Spark StructType schema to a BigQuery Schema.

        Args:
            struct_type (StructType): The Spark StructType schema.

        Returns:
            List[google.cloud.bigquery.SchemaField]: The corresponding BigQuery schema.
        """
        spark_to_bq_mapping = {
            IntegerType: "INT64",
            DecimalType: "NUMERIC",
            DoubleType: "FLOAT64",
            StringType: "STRING",
            BooleanType: "BOOL",
            TimestampType: "TIMESTAMP",
            DateType: "DATE",
        }

        fields = []
        for field in struct_type.fields:
            bq_type = spark_to_bq_mapping.get(type(field.dataType))
            if not bq_type:
                raise ValueError(f"Unsupported Spark data type: {field.dataType}")
            fields.append(
                SchemaField(
                    name=field.name,
                    field_type=bq_type,
                    mode="NULLABLE" if field.nullable else "REQUIRED"
                )
            )

        return fields

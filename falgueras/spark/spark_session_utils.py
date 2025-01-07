from pyspark.sql import SparkSession

from falgueras.common.enums import ExecutionMode


class SparkSessionUtils:
    """Utility class for creating and configuring Spark sessions."""

    @staticmethod
    def get_spark_session(app_name: str,
                          execution_mode: str = ExecutionMode.LOCAL,
                          timezone: str = "Europe/Sofia") -> SparkSession:
        """
        Creates and configures a Spark session.

        Args:
            app_name (str): Name of the Spark application.
            execution_mode (str): Execution mode, either "LOCAL" or "CLUSTER".
            timezone (str): Timezone to set for the Spark session.

        Returns:
            SparkSession: Configured Spark session.
        """
        if execution_mode == ExecutionMode.LOCAL:
            spark = (SparkSession.builder
                     .master("local[*]")
                     .appName(app_name)
                     .config("spark.jars.packages",
                             "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.41.1,"
                             "org.apache.spark:spark-avro_2.12:3.5.2")
                     .getOrCreate())
        else:
            spark = (SparkSession.builder
                     .appName(app_name)
                     .getOrCreate())

        # Common configurations
        spark.conf.set("viewsEnabled", "true")
        spark.conf.set("spark.sql.session.timeZone", timezone)

        return spark

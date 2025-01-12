from pyspark.sql import SparkSession

from falgueras.common.enums import ExecutionMode
from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


class SparkSessionUtils:
    """Utility class for creating and configuring Spark sessions."""

    @staticmethod
    def log_spark_config(spark: SparkSession) -> None:
        logger.info(f"""Spark session has been created with: 
            --driver-cores: {spark.sparkContext.getConf().get('spark.driver.cores')}
            --driver-memory: {spark.sparkContext.getConf().get('spark.driver.memory')}
            --num-executors: {spark.sparkContext.getConf().get('spark.executor.instances')}
            --executor-cores: {spark.sparkContext.getConf().get('spark.executor.cores')}
            --executor-memory: {spark.sparkContext.getConf().get('spark.executor.memory')}
            --timezone: {spark.sparkContext.getConf().get('spark.sql.session.timeZone')}""")

    @staticmethod
    def get_spark_session(app_name: str,
                          execution_mode: ExecutionMode = ExecutionMode.LOCAL,
                          timezone: str = "America/Bogota") -> SparkSession:
        """
        Creates and configures a Spark session.

        Jar gcs-connector-hadoop3-2.2.19.jar is download by URL instead of being retrieved from Maven to avoid
        dependency conflict in local executing mode.

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
                     .config("spark.jars", "https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop3-2.2.19.jar")
                     .config("spark.jars.packages",
                             "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.41.1,"
                             "org.apache.spark:spark-avro_2.12:3.5.2")
                     .getOrCreate())

            spark._jsc.hadoopConfiguration().set('fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem')

        else:
            spark = (SparkSession.builder
                     .appName(app_name)
                     .getOrCreate())

        # common configurations
        spark.conf.set("viewsEnabled", "true")
        spark.conf.set("spark.sql.session.timeZone", timezone)

        SparkSessionUtils.log_spark_config(spark)

        return spark

    @staticmethod
    def create_spark_session_standalone(app_name: str,
                                        master: str = "local",
                                        executors: int = 2,
                                        executor_cores: int = 4,
                                        executor_memory: int = 8,
                                        driver_cores: int = 2,
                                        driver_memory: int = 4):

        spark = SparkSession.builder.appName(app_name) \
            .master(master) \
            .config("spark.driver.cores", f"{driver_cores}G") \
            .config("spark.driver.memory", f"{driver_memory}G") \
            .config("spark.executor.memory", f"{executor_memory}G") \
            .config("spark.executor.instances", executors) \
            .config("spark.executor.cores", executor_cores) \
            .getOrCreate()

        SparkSessionUtils.log_spark_config(spark)

        return spark

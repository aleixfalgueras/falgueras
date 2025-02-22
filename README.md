
# Falgueras 🪴

[![PyPI version](https://img.shields.io/pypi/v/falgueras?color=4CBB17)](https://pypi.org/project/falgueras/)

Development framework for Python projects involving GCP, Pandas, and Spark. 

The main goal is to accelerate development of data-driven projects by offering a unified framework 
for developers with different backgrounds, from software and data engineers to data scientists.

## Set up

Base package: `pip install falgueras` (requieres Python>=3.10)

PySpark dependencies: `pip install falgueras[spark]` (PySpark 3.5.2)

PySpark libraries are optional to keep the package lightweight and because in most cases 
they are already provided by the environment. If you don't use falgueras PySpark
dependencies, keep in mind that versions of the numpy, pandas and pyarrow packages were 
tested against PySpark version 3.5.2. Behavior with other versions may change.

### Run Spark 3.5.2 applications locally in Windows from IntelliJ

_try fast fail fast learn fast_

For local Spark execution in Windows, the following environment variables must be set appropriately: 
- SPARK_HOME; version spark-3.5.2-bin-hadoop3.
- HADOOP_HOME; same value than SPARK_HOME.
- JAVA_HOME; recommended Java SDK 11.
- PATH += %HADOOP_HOME%\bin, %JAVA_HOME%\bin.

%HADOOP_HOME%\bin must contain files winutils.exe and hadoop.dll, download from 
[here](https://github.com/kontext-tech/winutils/blob/master/hadoop-3.3.0/bin).

Additionally, add `findspark.init()` at the beginning of the script in order to set and add 
environment variables and dependencies to sys.path.

### Connect to BigQuery from Spark

As shown in the `spark_session_utils.py`, the SparkSession used must include the jar
`com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.41.1` 
in order to communicate with BigQuery.

## Packages

### `falgueras.common`

Shared code between other packages and utils functions: datetime, json, enums, logging.

### `falgueras.gcp`

The functionalities of various Google Cloud Platform (GCP) services are encapsulated within 
custom client classes. This approach enhances clarity and promotes better encapsulation. 
File `services_toolbox.py` contains standalone functions to interact with GCP services. If there's
more than one function for a particular service, they must be grouped in a custom client class.

For instance, Google Cloud Storage (GCS) operations are wrapped in the `gcp.GcsClient` class,
which has an attribute that holds the actual `storage.Client` object from GCS. Multiple `GcsClient` 
instances can share the same `storage.Client` object.

### `falgueras.pandas`

Pandas related code.

The pandas_repo.py file provides a modular and extensible framework for handling pandas DataFrame operations 
across various storage systems. Using the `PandasRepo` abstract base class and `PandasRepoProtocol`, 
it standardizes read and write operations while enabling custom implementations for specific backends 
such as BigQuery (`BqPandasRepo`). These implementations encapsulate backend-specific logic, allowing 
users to interact with data sources using a consistent interface.

`BqPandasRepo` uses `gcp.BqClient` to interact with BigQuery.

### `falgueras.spark`

Spark related code.

In the same way than the pandas_repo.py file, the spark_repo.py file provides a modular and extensible 
framework for handling Spark DataFrame operations across various storage systems. Using the `SparkRepo` abstract base 
class and `SparkRepoProtocol`, it standardizes read and write operations while enabling custom implementations for 
specific backends such as BigQuery (`BqSparkRepo`). These implementations encapsulate backend-specific logic, allowing
users to interact with data sources using a consistent interface.

In contrast to `BqPandasRepo`, `BqSparkRepo` uses connectors 
gcs-connector-hadoop3 and spark-bigquery-with-dependencies in order to interact with BigQuery.

# Falgueras 🪴

Common code for Python projects involving GCP, Pandas, and Spark. 

The main goal is to accelerate development of data-driven projects by providing a common framework for developers
with different backgrounds: software engineers, big data engineers and data scientists.

## Packages

### `falgueras.common`

Shared code between other packages: datetime, json, enums, logging.

### `falgueras.gcp`

The functionalities of various Google Cloud Platform (GCP) services are encapsulated within 
custom client classes. This approach enhances clarity and promotes better encapsulation.

For instance, Google Cloud Storage (GCS) operations are wrapped in the `gcp.GcsClient` class,
which has an attribute that holds the actual `storage.Client` object from GCS. Multiple `GcsClient` 
instances can share the same `storage.Client` object.

### `falgueras.pandas`

Pandas related code.

The pandas_repo.py file provides a modular and extensible framework for handling pandas DataFrame operations 
across various storage systems. Using the `PandasRepo` abstract base class and `PandasRepoProtocol`, 
it standardizes read and write operations while enabling custom implementations for specific backends 
such as BigQuery (`BqPandasRepo`).

These implementations encapsulate backend-specific logic, allowing users to interact with data sources 
using a consistent interface. 
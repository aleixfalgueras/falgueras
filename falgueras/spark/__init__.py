
try:
    import pyspark
except ImportError:
    raise ImportError(
        "Spark utilities require pyspark. Install with 'pip install falgueras[spark]'"
    )

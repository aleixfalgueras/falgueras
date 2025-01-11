from dataclasses import asdict

from pandas import DataFrame


def serialize_for_bq_struct(df: DataFrame, col_name: str) -> DataFrame:
    """
    Serializes a DataFrame column containing dataclass type objects into a format compatible with
    BigQuery's STRUCT (RECORD) field type. Objects must first be converted into dictionaries
    or lists of dictionaries to avoid serialization errors.
    """

    df[col_name] = df[col_name].apply(
        lambda elements:
        [asdict(element) for element in elements] if isinstance(elements, list)
        else asdict(elements)
    )

    return df
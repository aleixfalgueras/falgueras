from typing import Optional

from google.cloud import storage


class GcsClient:
    """
    A class to handle Google Cloud Storage (GCS) operations.
    """

    def __init__(self, client: Optional[storage.Client] = None):
        """
        Initializes the GCS client.

        Args:
            client (Optional[storage.Client]): An optional instance of the Google Cloud Storage Client.
                - If provided, this client instance will be used for all GCS operations.
                - If not provided, a new instance of `storage.Client` will be created.
        """
        self.client = storage.Client() if client is None else client

    def read_as_text(self, bucket: str, path: str) -> str:
        """
        Reads a file from a Google Cloud Storage bucket as text.

        Args:
            bucket (str): The name of the bucket.
            path (str): The path to the file within the bucket.

        Returns:
            str: The content of the file as a string.

        Raises:
            RuntimeError: If the file cannot be read.
        """
        try:
            blob = self.client.get_bucket(bucket).blob(path)
            return blob.download_as_text()
        except Exception as e:
            raise RuntimeError(f"Failed to read {path} from {bucket}: {e}")

    def write_string(self, bucket: str, path: str, data: str, content_type: str = "text/csv") -> None:
        """
        Writes a string to a Google Cloud Storage bucket.

        Args:
            bucket (str): The name of the bucket.
            path (str): The path where the file should be written within the bucket.
            data (str): The string data to be written.
            content_type (str): The MIME type of the content.

        Raises:
            RuntimeError: If the file cannot be written.
        """
        if not bucket or not path:
            raise ValueError("Bucket and path must be non-empty strings.")

        try:
            blob = self.client.get_bucket(bucket).blob(path)
            blob.upload_from_string(data, content_type=content_type)
        except Exception as e:
            raise RuntimeError(f"Failed to write data to {path} in {bucket}: {e}")

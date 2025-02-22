from typing import Optional

from google.cloud import storage

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


class GcsClient:
    """A class to handle Google Cloud Storage (GCS) operations."""

    def __init__(self, client: Optional[storage.Client] = None):
        """
        Initializes the GCS client.

        Args:
            client (Optional[storage.Client]): An optional instance of the Google Cloud Storage Client.
                - If provided, this client instance will be used for all GCS operations.
                - If not provided, a new instance of `storage.Client` will be created.
        """
        self.client = storage.Client() if client is None else client

    def exists_object(self, filename: str, bucket_name: str) -> bool:
        """Checks if an object exists in a specified Google Cloud Storage bucket."""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(filename)

            return blob.exists()

        except Exception as e:
            logger.error(e)
            raise RuntimeError(f"Failed to check existence of {filename} in bucket {bucket_name}: {e}")

    def read_text(self, bucket_name: str, path: str) -> str:
        """
        Reads a file from a Google Cloud Storage bucket as text.
        Returns the content of the file as a string.
        """
        try:
            blob = self.client.get_bucket(bucket_name).blob(path)
            return blob.download_as_text()

        except Exception as e:
            logger.error(e)
            raise RuntimeError(f"Failed to read {path} from {bucket_name}: {e}")

    def download_file(self,
                      bucket_name: str,
                      filename: str,
                      target_filename: str = None) -> None:
        """
        Download an object into a named file, if not target_filename is provided, the same
        object name is used for the naming the file.
        """
        try:
            if not target_filename:
                target_filename = filename

            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.download_to_filename(target_filename)

        except Exception as e:
            logger.error(e)
            raise RuntimeError(f"Failed to download '{filename}' from {bucket_name}: {e}")

    def read_bytes(self, bucket_name: str, filename: str) -> bytes:
        """Reads a file from a Google Cloud Storage bucket as bytes."""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(filename)

            return blob.download_as_bytes()

        except Exception as e:
            logger.error(e)
            raise Exception(f"Error reading PDF from GCS: {str(e)}")

    def write_string(self,
                     bucket_name: str,
                     path: str,
                     data: str,
                     content_type: str = "text/csv",
                     content_encoding: Optional[str] = "utf-8") -> str:
        """
        Writes a string to a Google Cloud Storage bucket.

        Args:
            bucket_name (str): The name of the bucket.
            path (str): The path where the file should be written within the bucket.
            data (str): The string data to be written.
            content_type (str): The MIME type of the content.
            content_encoding (Optional[str]): Content encoding of the file

        Raises: Return public url of the written object.
        """
        if not bucket_name or not path:
            raise ValueError("Bucket and path must be non-empty strings.")

        try:
            blob = self.client.get_bucket(bucket_name).blob(path)
            blob.content_encoding = content_encoding

            logger.info(f"Writing string data file (type: {content_type}, encoding: {content_encoding}) in "
                        f"gs://{bucket_name}/{path}")
            blob.upload_from_string(data, content_type=content_type)

            return blob.public_url

        except Exception as e:
            logger.error(e)
            raise RuntimeError(f"Failed to write data to {path} in {bucket_name}: {e}")

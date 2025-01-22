from io import BytesIO
from typing import Optional

import PyPDF2
from google.cloud import storage


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

    def read_text(self, bucket: str, path: str) -> str:
        """
        Reads a file from a Google Cloud Storage bucket as text.
        Returns the content of the file as a string.
        """
        try:
            blob = self.client.get_bucket(bucket).blob(path)
            return blob.download_as_text()
        except Exception as e:
            raise RuntimeError(f"Failed to read {path} from {bucket}: {e}")

    def read_pdf(self, bucket_name: str, file_name: str) -> str:
        """
        Read and extract text from a PDF stored in GCS.
        Returns: Extracted text from the PDF.
        """
        try:

            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(file_name)

            content = blob.download_as_bytes()
            pdf_file = BytesIO(content)

            reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'

            return text

        except Exception as e:
            raise Exception(f"Error reading PDF from GCS: {str(e)}")

    def write_string(self, bucket_name: str, path: str, data: str, content_type: str = "text/csv") -> str:
        """
        Writes a string to a Google Cloud Storage bucket.

        Args:
            bucket_name (str): The name of the bucket.
            path (str): The path where the file should be written within the bucket.
            data (str): The string data to be written.
            content_type (str): The MIME type of the content.

        Raises: Return public url of the written object.
        """
        if not bucket_name or not path:
            raise ValueError("Bucket and path must be non-empty strings.")

        try:
            blob = self.client.get_bucket(bucket_name).blob(path)
            blob.upload_from_string(data, content_type=content_type)

            return blob.public_url

        except Exception as e:
            raise RuntimeError(f"Failed to write data to {path} in {bucket_name}: {e}")

    def exists_object(self, filename: str, bucket_name: str) -> bool:
        """Checks if an object exists in a specified Google Cloud Storage bucket."""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(filename)
            
            return blob.exists()
        
        except Exception as e:
            raise RuntimeError(f"Failed to check existence of {filename} in bucket {bucket_name}: {e}")
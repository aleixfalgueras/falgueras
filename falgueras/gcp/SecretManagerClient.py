import json
from typing import Optional

from google.cloud import secretmanager
from google.cloud.secretmanager_v1 import SecretManagerServiceClient

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


class SecretManagerClient:
    """
    A client wrapper for Google Secret Manager to simplify secret retrieval.

    Attributes:
        client (SecretManagerServiceClient): The underlying Google Secret Manager client.
    """

    def __init__(self, client: Optional[SecretManagerServiceClient] = None):
        """
        Initializes the SecretManagerClient.

        Args:
            client (Optional[SecretManagerServiceClient]): An existing SecretManagerServiceClient instance.
                If not provided, a new instance is created.
        """
        self.client = secretmanager.SecretManagerServiceClient() if client is None else client

    def get_secret(self, secret_name: str, project_id: str) -> dict:
        """
        Retrieves the latest version of a secret from Google Secret Manager.

        Args:
            secret_name (str): The name of the secret to retrieve.
            project_id (str): The Google Cloud project ID where the secret is stored.

        Returns:
            dict: The secret data as a dictionary.
        """
        secret_full_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        logger.info(f"Reading secret: {secret_full_name}")

        response = self.client.access_secret_version(name=secret_full_name)
        key_data = response.payload.data.decode("UTF-8")

        return json.loads(key_data)

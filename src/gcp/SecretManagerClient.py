import json
from typing import Optional

from google.cloud import secretmanager
from google.cloud.secretmanager_v1 import SecretManagerServiceClient

from src.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


class SecretManagerClient:

    def __init__(self, client: Optional[SecretManagerServiceClient] = None):
        self.client = secretmanager.SecretManagerServiceClient() if client is None else client

    def get_secret(self, secret_name: str, project_id: str) -> dict:
        secret_full_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        logger.info(f"Reading secret: {secret_full_name}")

        response = self.client.access_secret_version(name=secret_full_name)
        key_data = response.payload.data.decode("UTF-8")

        return json.loads(key_data)

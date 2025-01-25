from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)

class GoogleDriveClient:
    """
    A class to handle interactions with Google Drive.
    """

    @staticmethod
    def write_file_in_google_drive(file_path: str,
                                   target_filename: str,
                                   mimetype: str,
                                   folder_id: str,
                                   service_account_key: dict,
                                   scopes=None) -> str:
        """
        Uploads a file to Google Drive using a service account for authentication.

        :param file_path:
            The local file path of the file to be uploaded.
        :param target_filename:
            The desired name for the file in Google Drive.
        :param mimetype:
            The MIME type of the file (e.g., 'text/csv', 'application/pdf').
        :param folder_id:
            The ID of the Google Drive folder where the file will be stored.
        :param service_account_key:
            Service account JSON key as dict.
        :param scopes:
            A list of scopes defining the permissions for Google Drive API access.

        :return:
            The URL of the file created in Google Drive.
        """
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/drive.file"]

        credentials = service_account.Credentials.from_service_account_info(service_account_key, scopes=scopes)

        drive_service = build("drive", "v3", credentials=credentials)
        file_metadata = {"name": target_filename, "parents": [folder_id]}
        media = MediaFileUpload(file_path, mimetype)

        logger.info(f"Writing file {file_path} ({mimetype}) in Google Drive's folder ID {folder_id} "
                    f"with name {target_filename} using service_account {credentials.service_account_email}")

        file_id = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        file_url = f"https://drive.google.com/file/d/{file_id['id']}/view"

        logger.info(f"New file created! File ID: {file_id['id']}, url: {file_url}")

        return file_url

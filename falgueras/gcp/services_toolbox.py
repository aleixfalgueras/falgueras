from google.cloud import translate

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)


def translate_text(project_id: str, text: str, source_language_code: str, target_language: str) -> str:
    """
    If the source_language_code isn't specified, the API attempts to identify the source language
    automatically and returns the source language within the response.

    :param project_id: GCP project ID
    :param text: text to translate
    :param source_language_code: ISO-639 language code
    :param target_language: ISO-639 language code
    :return: text translated
    """
    try:
        client = translate.TranslationServiceClient()
        location = "global"
        parent = f"projects/{project_id}/locations/{location}"

        logger.info(f"Translating text from language '{source_language_code}' to '{target_language}'")
        logger.debug(text)

        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": source_language_code,
                "target_language_code": target_language,
            }
        )

        return response.translations[0].translated_text

    except Exception as e:
        raise Exception(f"Translation error (from {source_language_code} to {target_language}): {str(e)}")

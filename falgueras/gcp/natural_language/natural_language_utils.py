from typing import Optional

from google.cloud import language_v2, language_v1

from falgueras.common.logging_utils import get_colored_logger
from falgueras.gcp.natural_language.model import EntityNl

logger = get_colored_logger(__name__)


def get_text_document(text: str, language_code: Optional[str] = None, version: str = "2") -> dict:
    type_ = language_v2.Document.Type.PLAIN_TEXT if version == "2" else language_v1.Document.Type.PLAIN_TEXT

    if language_code is None:  # let the API figure it out
        document = {"content": text,
                    "type_": type_}
    else:
        if version == "1":
            document = {"content": text,
                        "type_": type_,
                        "language": language_code}
        else:
            document = {"content": text,
                        "type_": type_,
                        "language_code": language_code}

    return document


def remove_duplicate_entities(entities: list[EntityNl]) -> list[EntityNl]:
    """
    Removes duplicates from a list of EntityNl objects based on the 'name' attribute.
    Keeps the object with the highest 'salience' value for each name.

    Args:
        entities (List[EntityNl]): The list of EntityNl objects.

    Returns:
        List[EntityNl]: A list with duplicates removed based on the criteria.
    """
    unique_entities = {}

    for entity in entities:
        if entity.name not in unique_entities:
            unique_entities[entity.name] = entity
        else:
            logger.info(f"Duplicated entity detected: {entity} - {unique_entities[entity.name]}")
            if entity.salience > unique_entities[entity.name].salience:
                logger.info(f"Updating entity reference {entity.name} with new entity: {entity}")
                unique_entities[entity.name] = entity

    return list(unique_entities.values())

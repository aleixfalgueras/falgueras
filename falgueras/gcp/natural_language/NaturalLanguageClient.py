from typing import Optional

from google.cloud import language_v1
from google.cloud import language_v2

from falgueras.common.logging_utils import get_colored_logger
from falgueras.gcp.natural_language.model import EntityNl, SentimentNl, CategoryNl
from falgueras.gcp.natural_language.natural_language_utils import remove_duplicate_entities

logger = get_colored_logger(__name__)


class NaturalLanguageClient:
    """Some functionalities, like analyze_entity_sentiment, are only available in the language_v1 client"""

    LANGUAGES_NOT_SUPPORTED = ["de"]

    def __init__(self,
                 client_v1: Optional[language_v1.LanguageServiceClient] = None,
                 client_v2: Optional[language_v2.LanguageServiceClient] = None):

        self.client_v1 = language_v1.LanguageServiceClient() if client_v1 is None else client_v1
        self.client_v2 = language_v2.LanguageServiceClient() if client_v2 is None else client_v2

    def classify_text(self, document: dict) -> list[CategoryNl]:
        logger.info("Calling classify_text from Google Natural Language API...")

        response = self.client_v2.classify_text(request={"document": document})

        text_categories = []
        for category in response.categories:
            text_categories.append(CategoryNl(category.name, category.confidence, category.severity))

        return text_categories

    def analyze_sentiment(self, document: dict, encoding_type=language_v2.EncodingType.UTF8) -> SentimentNl:
        logger.info("Calling analyze_sentiment from Google Natural Language API...")

        try:
            response = self.client_v2.analyze_sentiment(
                request={"document": document, "encoding_type": encoding_type}
            ).document_sentiment
        except Exception as exc:
            logger.error(f"Couldn't analyze sentiment of document: \n{document}")
            raise exc

        return SentimentNl(response.score, response.magnitude)

    def analyze_entities(self, document: dict, encoding_type=language_v2.EncodingType.UTF8) -> list[EntityNl]:
        """Caution: May return entities with the same name"""
        logger.info("Calling analyze_entities from Google Natural Language API...")

        response = self.client_v2.analyze_entities(
            request={"document": document, "encoding_type": encoding_type}
        )

        entities = []
        for entity in response.entities:
            entities.append(
                EntityNl(name=entity.name,
                         type=str(entity.type_).removeprefix("Type."),
                         probability=round(entity.mentions[0].probability, 2))
            )

        return entities

    def analyze_entity_salience(self,
                                document: dict,
                                encoding_type=language_v1.EncodingType.UTF8,
                                remove_duplicates: bool = False) -> list[EntityNl]:
        """Caution: May return entities with the same name"""
        logger.info("Calling analyze_entity_sentiment from Google Natural Language API...")

        if document['language'] in self.LANGUAGES_NOT_SUPPORTED:
            logger.warn(f"Document '{document}' ignored because language is not supported, "
                        f"returning empty list.")
            return []

        try:
            response = self.client_v1.analyze_entity_sentiment(
                request={"document": document, "encoding_type": encoding_type}
            )
        except Exception as exc:
            logger.error(f"Couldn't analyze entity sentiment of document: \n{document}")
            raise exc

        entities = []
        for entity in response.entities:
            entities.append(
                EntityNl(name=entity.name,
                         type=str(entity.type_).removeprefix("Type."),
                         salience=round(entity.salience, 4))
            )

        if remove_duplicates:
            entities = remove_duplicate_entities(entities)

        return entities

    @staticmethod
    def log_analyze_entity_sentiment_response(response):
        logger.info("#### Analyze entity sentiment ####")

        for entity in response.ENTITIES:
            logger.info(f"Representative name for the entity: {entity.NAME}")
            logger.info(f"Entity type: {language_v1.Entity.Type(entity.type_).name}")

            # salience: the fact of being important to or connected with what is happening or being discussed
            logger.info(f"Salience score: {entity.salience}")

            sentiment = entity.sentiment  # aggregate sentiment expressed for this entity
            logger.info(f"Entity sentiment score: {sentiment.score}, magnitud: {sentiment.magnitude}")

            # Loop over the metadata associated with entity. For many known entities,
            # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
            # Some entity types may have additional metadata, e.g. ADDRESS entities
            # may have metadata for the address street_name, postal_code, et al.
            for metadata_name, metadata_value in entity.metadata.items():
                logger.info(f"{metadata_name} = {metadata_value}")

            # Loop over the mentions of this entity in the input document
            for mention in entity.MENTIONS:
                logger.info(f"Mention text: {mention.TEXT.content}")
                logger.info("Mention type: {}".format(language_v1.EntityMention.Type(mention.type_).name))

from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoryNl:
    """
    Represents a category returned from the text classifier.

    Attributes:
        name (str):
            The name of the category representing the
            document.
        confidence (float):
            The classifier's confidence of the category.
            Number represents how certain the classifier is
            that this category represents the given text.
        severity (float):
            Optional. The classifier's severity of the category. This is
            only present when the ModerateTextRequest.ModelVersion is
            set to MODEL_VERSION_2, and the corresponding category has a
            severity score.
    """
    name: str
    confidence: float
    severity: Optional[float] = None


@dataclass
class SentimentNl:
    """
    Represents sentiment information derived from the Google Natural Language API analysis.

    Attributes:
        score (float):
            Indicates the overall sentiment of the document on a scale from `-1.0` to `1.0`:
              - `-1.0` represents extremely negative sentiment.
              - `0.0` represents neutral sentiment.
              - `1.0` represents extremely positive sentiment.
            This value reflects the emotional polarity of the text but does not specify
            individual emotions (e.g., "angry" or "sad" are both simply categorized as negative).

            Notes on `score`:
              - A value near `0.0` may indicate neutrality or mixed emotions.
              - Use the `magnitude` attribute to disambiguate neutrality from mixed emotions.

        magnitude (float):
            Indicates the strength of emotional content in the document. This value ranges
            from `0.0` to `+inf`, with:
              - `0.0` indicating no emotional content.
              - Higher values indicating stronger emotions, regardless of polarity.

            Notes on `magnitude`:
              - Proportional to the length of the document.
              - Higher magnitude values for documents with mixed emotions suggest conflicting
                positive and negative sentiments canceling out the `score`.

    General Usage:
        - Use `score` to determine the overall sentiment polarity (positive, neutral, negative).
        - Use `magnitude` to assess the intensity of emotional content, particularly in cases
          where the `score` is close to `0.0`.
        - When comparing documents of different lengths, factor in `magnitude` to normalize
          the analysis, as longer documents tend to have higher magnitude values.

    Example:
        A document with:
          - `score = 0.0` and `magnitude = 0.1` is likely neutral with minimal emotional content.
          - `score = 0.0` and `magnitude = 2.0` suggests mixed positive and negative sentiments.
          - `score = -0.5` and `magnitude = 1.5` indicates a moderately negative document
            with significant emotional content.
    """

    score: float  # Overall sentiment polarity
    magnitude: float  # Intensity of emotional content


@dataclass
class EntityNl:
    """
    Represents an entity recognized by the Google Natural Language API.

    Attributes:
        name (str):
            The name of the entity as identified in the text. For example,
            a person, location, organization, or other recognized noun.

        type (str):
            The type or category of the entity. Common types include PERSON, LOCATION,
            ORGANIZATION, EVENT, WORK_OF_ART, CONSUMER_GOOD, and other classifications
            as defined by the Google Natural Language API.

        probability (Optional[float]):
            The likelihood that the entity mention corresponds to the specified entity type.
            This value is a float in the range [0.0, 1.0], where:
              - 0.0 represents no confidence,
              - 1.0 represents full confidence.
            Default is 1.0, indicating maximum confidence in the entity type.

        salience (Optional[float]):
            A measure of the importance or centrality of the entity to the analyzed text.
            This value is a float in the range [0.0, 1.0], where:
              - 0.0 represents minimal importance,
              - 1.0 represents maximum importance.
            A higher salience indicates that the entity is more central to the meaning
            of the text. Default is None, indicating that salience was not calculated or provided.
    """

    name: str
    type: str
    probability: Optional[float] = 1.0  # Default is full confidence.
    salience: Optional[float] = None  # Default is None, meaning not provided.

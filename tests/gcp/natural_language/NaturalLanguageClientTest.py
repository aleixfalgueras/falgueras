import unittest

from google.cloud import language_v2

from src.gcp.natural_language.NaturalLanguageClient import NaturalLanguageClient
from src.gcp.natural_language.model import EntityNl, SentimentNl, CategoryNl


class NaturalLanguageClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nl_client = NaturalLanguageClient()

        cls.test_text = """
        ‘The Fellowship Of The Ring’ is the first film in ‘The Lord Of The Rings’ series at sees 
        aging wizard Gandalf (Ian McKellan) realise that the power of a very special ring is starting to 
        get the best of a curious hobbit called Bilbo Baggins (Ian Holm). Gandalf asks young hobbit, 
        Frodo Baggins (Elijah Wood) to look after the ring but when it is soon realised that the evil 
        Saruman (Christopher Lee) is raising up the dark forces and is desperate to gain the ring Gandalf 
        instead decides that it is time for Frodo to go and destroy the ring in the fires of Mordor.
        Soon Frodo is joined by the likes of Samwise Gangee (Sean Astin), Peregin Took (Billy Boyd) and 
        Meriadoc Brandybuck (Dominic Monaghan) on a journey where they need others including Aragorn 
        (Viggo Mortensen) and Legolas Greenleaf (Orlando Bloom) to protect them. But with danger at every 
        corner and never knowing who to trust this is never going to be an easy journey.
        """
        cls.test_document = {"content": cls.test_text, "type_": language_v2.Document.Type.PLAIN_TEXT}

    def test_classify_text(self):
        result = self.nl_client.classify_text(self.test_document)

        for category in result:
            print(category)
            self.assertIsInstance(category, CategoryNl)

    def test_analyze_entities(self):
        entities = self.nl_client.analyze_entities(self.test_document)

        self.assertIsInstance(entities[0], EntityNl)
        for entity in entities:
            print(f"{entity.name}, {entity.type}, probability: {entity.probability}, salience: {entity.salience}")
            self.assertTrue(hasattr(entity, 'name'))
            self.assertTrue(hasattr(entity, 'type'))

    def test_analyze_sentiment(self):
        result = self.nl_client.analyze_sentiment(self.test_document)

        self.assertIsInstance(result, SentimentNl)

    def test_analyze_entity_sentiment(self):
        entities = self.nl_client.analyze_entity_salience(self.test_document)

        self.assertIsInstance(entities[0], EntityNl)
        for entity in sorted(entities, key=lambda _entity: _entity.NAME):
            print(f"{entity.name}, {entity.type}, probability: {entity.probability}, salience: {entity.salience}")
            self.assertTrue(hasattr(entity, 'name'))
            self.assertTrue(hasattr(entity, 'salience'))


if __name__ == "__main__":
    unittest.main()

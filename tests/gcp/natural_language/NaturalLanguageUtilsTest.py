import unittest

from falgueras.gcp.natural_language.model import EntityNl
from falgueras.gcp.natural_language.natural_language_utils import remove_duplicate_entities


class NaturalLanguageUtilsTest(unittest.TestCase):

    def test_remove_duplicate_entities(self):
        entites = [
            EntityNl("Pepito", "PERSON", salience=0.1),
            EntityNl("Pepito", "PERSON", salience=0.2),
            EntityNl("Juan", "PERSON", salience=0.5)
        ]

        unique_entites_expected = [
            EntityNl("Pepito", "PERSON", salience=0.2),
            EntityNl("Juan", "PERSON", salience=0.5)
        ]

        unique_entites = remove_duplicate_entities(entites)

        self.assertCountEqual(unique_entites_expected, unique_entites)


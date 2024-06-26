import os
import unittest

from gws_biota._helper.rhea import Rhea
from gws_core import Settings


class TestModel(unittest.TestCase):

    def test_db_object(self):
        settings = Settings.get_instance()
        testdata_path = os.path.join(
            settings.get_variable("gws_biota:testdata_dir"),
            '../_helper/data/'
        )

        list_reactions = Rhea.parse_reaction_from_file(testdata_path, 'rhea-reaction.txt')
        self.assertEqual(len(list_reactions), 12)
        self.assertEqual(list_reactions[0]['entry'], 'RHEA:10022')
        self.assertEqual(list_reactions[1]['substrates'], ["CHEBI:15377", "CHEBI:57951", "CHEBI:58349"])

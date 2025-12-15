from gws_biota import Reaction
from gws_biota.reaction.reaction_service import ReactionService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestReaction(BaseTestCase):
    def test_db_object(self):
        self.print("Reaction")
        params = dict(
            biodata_dir=testdata_path,
            rhea_reaction_file="rhea-reactions_test.txt",
            rhea_direction_file="rhea-directions-test.tsv",
            rhea2ecocyc_file="rhea2ecocyc-test.tsv",
            rhea2metacyc_file="rhea2metacyc-test.tsv",
            rhea2macie_file="rhea2macie_test.tsv",
            rhea2kegg_reaction_file="rhea2kegg_reaction_test.tsv",
            rhea2ec_file="rhea2ec-test.tsv",
            rhea2reactome_file="rhea2reactome_test.tsv",
        )

        ReactionService.create_reaction_db(**params)
        self.assertEqual(Reaction.get(Reaction.rhea_id == "RHEA:10022").master_id, "10020")
        self.assertEqual(Reaction.get(Reaction.rhea_id == "RHEA:10031").kegg_id, "R00279")

        rxn = Reaction.get(Reaction.rhea_id == "RHEA:58156")
        print(rxn.data)
        print(rxn.ft_names)
        print(rxn.ft_tax_ids)
        print(rxn.ft_ec_numbers)
        print(rxn.layout)

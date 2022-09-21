
import pickle

import networkx as nx
import numpy
from gws_biota import BaseTestCaseUsingFullBiotaDB, Compound, Unicell
from gws_biota.unicell.unicell_service import UnicellService
from gws_core import BaseTestCase, Settings
from scipy import sparse

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")


class TestUnicell(BaseTestCaseUsingFullBiotaDB):

    def test_unicell(self):
        uc = UnicellService.create_unicell()
        tf = uc.are_connected("CHEBI:57604", "CHEBI:58272")  # -> true
        tf = uc.are_connected("CHEBI:57604", "CHEBI:58248")  # -> true
        self.assertTrue(tf)
        tf = uc.are_connected("CHEBI:57604", "CHEBI:58289", )  # -> true
        self.assertTrue(tf)
        tf = uc.are_connected("CHEBI:57604", "CHEBI:58289")  # -> true
        self.assertTrue(tf)

        path = uc.shortest_path("CHEBI:57604", "CHEBI:58289")
        #self.assertEqual( path, ['CHEBI:57604', 'CHEBI:58272', 'CHEBI:58289'])
        self.assertEqual(
            path == ['CHEBI:57604', 'CHEBI:58248', 'CHEBI:58289'] or \
            path == ['CHEBI:57604', 'CHEBI:58272', 'CHEBI:58289']
        )

        print(path)

        e = uc.get_edge(path[0], path[1])
        print(e)
        # self.assertEqual(e.data, {'rhea_id': 'RHEA:23332', 'dg_prime': 1})

        # RHEA:16845: (2R)-3-phosphoglycerate + GTP = (2R)-3-phospho-glyceroyl phosphate + GDP
        # RHEA:10336: citrate = D-threo-isocitrate
        # RHEA:16845: acetyl-CoA + H2O + oxaloacetate = citrate + CoA + H+
        g = uc.get_subgraph(['RHEA:23332', 'RHEA:10336', 'RHEA:16845'])

        print(g.nodes)
        self.assertTrue('CHEBI:16947' in g.nodes)  # citrate(3−)
        self.assertTrue('CHEBI:57604' in g.nodes)  # 3-phosphonato-D-glyceroyl phosphate(4−)
        self.assertTrue('CHEBI:16452' in g.nodes)  # oxaloacetate(2−)
        self.assertTrue('CHEBI:57288' in g.nodes)  # acetyl-CoA(4−)
        self.assertTrue('CHEBI:58272' in g.nodes)  # 3-phosphonato-D-glycerate(3−)
        self.assertTrue('CHEBI:15562' in g.nodes)  # D-threo-isocitrate(3−)
        self.assertEqual(len(g.nodes), 6)

        print(g.edges)
        self.assertEqual(len(g.edges), 4)

    def test_ecoli_unicell(self):
        tax_id = "562"  # ecoli
        uc = UnicellService.create_unicell(tax_id)
        print(uc.get_graph())

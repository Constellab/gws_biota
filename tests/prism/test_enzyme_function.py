import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.db.enzyme import Enzyme
from biota.db.protein import Protein
from biota.db.enzyme_function import EnzymeFunction

settings = Settings.retrieve()
testdata_path = settings.get_data("biota:testdata_dir")

class TestEnzyme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Protein.drop_table()
        EnzymeFunction.drop_table()
        EnzymeFunction.create_table()
   
    @classmethod
    def tearDownClass(cls):
        pass

    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            brenda_file = "brenda_test.txt",
            bkms_file   = "bkms_test.csv",
        )

        EnzymeFunction.create_enzyme_function_db(**params)

        enzo = EnzymeFunction.select().join(Enzyme).where(Enzyme.ec == '1.4.3.7')
        self.assertEqual(enzo[0].organism, 'Candida boidinii')

        self.assertEqual(len(enzo[0].params('CF')), 1)
        self.assertEqual(enzo[0].params('CF')[0].value, "FAD")
        self.assertEqual(enzo[0].params('CF')[0].refs, [1,3])
        self.assertEqual(enzo[0].params('CF')[0].full_refs, {'1': 4387700, '2': 'Urich, K.: D-Glutamtoxydase aus der Antennendruse des Flusskrebses Orconectes limosus: Reinigung und Charakterisierung. Z. Naturforsch. B (1968) 23, 1508-1511.', '3': 13583997})
        self.assertEqual(enzo[0].params('CF')[0].comments, "#1,2# cannot be replaced by FMN <1,3>")
        self.assertEqual(enzo[0].params('CF')[0].what, "cofactor")

        self.assertEqual(enzo[0].params('MW')[0].value, "43000")
        self.assertEqual(enzo[0].params('MW')[0].refs, [1])
        self.assertEqual(enzo[0].params('MW')[0].full_refs, {'1': 4387700, '2': 'Urich, K.: D-Glutamtoxydase aus der Antennendruse des Flusskrebses Orconectes limosus: Reinigung und Charakterisierung. Z. Naturforsch. B (1968) 23, 1508-1511.', '3': 13583997})
        self.assertEqual(enzo[0].params('MW')[0].comments, "#1# gel filtration <1>")
        self.assertEqual(enzo[0].params('MW')[0].what, "molecular weight")

        self.assertEqual(enzo[0].params('RE')[0].value, "D-glutamate + H2O + O2 = 2-oxoglutarate + NH3 + H2O2")
        self.assertEqual(enzo[0].params('RE')[0].what, "reaction catalyzed")
        self.assertEqual(enzo[0].params('RE')[0].comments, None)

        self.assertEqual(enzo[0].params('RT')[0].value, "oxidation")
        self.assertEqual(enzo[0].params('RT')[0].what, "reaction type")
        self.assertEqual(enzo[0].params('RT')[0].comments, None)

        self.assertEqual(enzo[0].params('RT')[1].value, "oxidative deamination")
        self.assertEqual(enzo[0].params('RT')[1].what, "reaction type")
        self.assertEqual(enzo[0].params('RT')[1].comments, None)

        self.assertEqual(enzo[0].params('RT')[2].value, "redox reaction")
        self.assertEqual(enzo[0].params('RT')[3].value, "reduction")
        self.assertEqual(enzo[0].params('RT')[1000].value, None)

        self.assertEqual(enzo[0].params('ST')[0].value, "cell culture")
        self.assertEqual(enzo[0].params('ST')[0].get("bto"), "BTO_0000214")

        self.assertEqual(enzo[0].params('UknownParam')[0].value, None)
        self.assertEqual(enzo[0].params('UknownParam')[1000].value, None)

        enzo = EnzymeFunction.select().join(Enzyme).where(Enzyme.ec == '3.5.1.43')
        self.assertEqual(enzo[0].organism, 'Bacillus circulans')
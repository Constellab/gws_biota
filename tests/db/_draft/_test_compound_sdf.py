import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.compound import Compound

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestCompound(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Compound.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #Compound.drop_table()
        pass
    
    def test_compound2(self):
        return
        biodata_dir = settings.get_dir("biota:chebi_biodata_dir")

        from biota._helper.chebi import Chebi as ChebiHelper
        ctf = ChebiHelper.read_sdf(biodata_dir, "./sdf/ChEBI_complete.sdf")

    def test_compound(self):
        return
        testdata_path = settings.get_dir("biota:testdata_dir")

        params = dict(
            biodata_dir = testdata_path,
            chebi_sdf_file = "chebi.sdf",
        )

        Compound.create_compound_db(**params)

        comp = Compound.get(Compound.chebi_id == 'CHEBI:90')
        self.assertEqual(comp.average_mass, 290.2681)
        self.assertEqual(comp.monoisotopic_mass, 290.07904)
        self.assertEqual(comp.inchi_key, 'PFTAWBLQPZVEMU-UKRRQHHQSA-N')

        print(comp.structure)


    # def test_db_object(self):
    #     return
    #     params = dict(
    #         biodata_dir = testdata_path,
    #         chebi_compound_file = "compounds_test.tsv",
    #         chebi_chemical_data_file =  "chemical_data_test.tsv",
    #     )

    #     Compound.create_compound_db(**params)
    #     self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:58321').name, 'L-allysine zwitterion')
    #     self.assertEqual(Compound.get(Compound.chebi_id == 'CHEBI:59789').name, 'S-adenosyl-L-methionine zwitterion')

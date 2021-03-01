import sys
import os
import unittest
import copy
import asyncio

from gws.settings import Settings
from biota.pathway import Pathway
from biota.compound import Compound

settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestPatwhays(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Compound.drop_table()
        Pathway.drop_table()
        
    @classmethod
    def tearDownClass(cls):
        Compound.drop_table()
        Pathway.drop_table()
        pass
    
    def test_db_object(self):
        cid = ["10033", "10036", "10049", "10055", "10093", "16027", "16284", "17111"]
        for _id in cid:
            c = Compound(chebi_id="CHEBI:"+_id)
            c.save()
        
        params = dict(
            biodata_dir = testdata_path,
            reactome_pathways_file =  'reactome_pathways.txt',
            reactome_pathway_relations_file = 'reactome_pathway_relations.txt',
            reactome_chebi_pathways_file = 'reactome_chebi.txt',
        )
        Pathway.create_pathway_db(**params)
        
        
        c = Compound.get(Compound.chebi_id == "CHEBI:10033")
        self.assertEqual( c.reactome_patwhay_id, "R-SSC-6806664" )
        self.assertEqual( c.reactome_patwhay.title, "Metabolism of vitamin K" )
        
        p = Pathway.get(Pathway.reactome_id == "R-BTA-1296025")
        self.assertEqual( p.title, "ATP sensitive Potassium channels" )
        
        p = Pathway.get(Pathway.reactome_id == "R-BTA-73843")
        self.assertEqual( p.title, "5-Phosphoribose 1-diphosphate biosynthesis" )
        self.assertEqual( len(p.ancestors), 1 )
        self.assertEqual( p.ancestors[0].title, "Pentose phosphate pathway" )
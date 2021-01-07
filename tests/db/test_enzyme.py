import sys
import os
import unittest

from gws.controller import Controller
from gws.settings import Settings
from biota.db.enzyme import Enzyme, Enzo
from biota.db.bto import BTO


settings = Settings.retrieve()
testdata_path = settings.get_dir("biota:testdata_dir")

class TestEnzyme(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Enzyme.drop_table()
        Enzo.drop_table()
        Enzyme.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        Enzyme.drop_table()
        Enzo.drop_table()
        BTO.drop_table()
        pass
    
    def test_db_object(self):
        params = dict(
            biodata_dir = testdata_path,
            brenda_file = "brenda_test.txt",
            bkms_file   = "bkms_test.csv",
        )
    
        bto = BTO(bto_id = 'BTO_0000214')
        bto.save()
        
        Enzyme.create_enzyme_db(**params)        
        enzyme = Enzyme.select().where(Enzyme.ec_number == '1.4.3.7')
        
        n = len(enzyme[0].params('ST'))
        bto_ids = []
        for i in range(0,n):
            bto_ids.append( enzyme[0].params('ST')[i].get("bto") )
        
        self.assertEqual(enzyme[0].bto[0].bto_id, 'BTO_0000214')
        
        self.assertEqual(enzyme[0].organism, 'Candida boidinii')
        self.assertEqual(enzyme[0].name, 'D-glutamate oxidase')

        self.assertEqual(len(enzyme[0].params('CF')), 1)
        self.assertEqual(enzyme[0].params('CF')[0].value, "FAD")
        self.assertEqual(enzyme[0].params('CF')[0].refs, [1,3])
        self.assertEqual(enzyme[0].params('CF')[0].full_refs, {'1': 4387700, '2': 'Urich, K.: D-Glutamtoxydase aus der Antennendruse des Flusskrebses Orconectes limosus: Reinigung und Charakterisierung. Z. Naturforsch. B (1968) 23, 1508-1511.', '3': 13583997})
        self.assertEqual(enzyme[0].params('CF')[0].comments, "#1,2# cannot be replaced by FMN <1,3>")
        self.assertEqual(enzyme[0].params('CF')[0].what, "cofactor")

        self.assertEqual(enzyme[0].params('MW')[0].value, "43000")
        self.assertEqual(enzyme[0].params('MW')[0].refs, [1])
        self.assertEqual(enzyme[0].params('MW')[0].full_refs, {'1': 4387700, '2': 'Urich, K.: D-Glutamtoxydase aus der Antennendruse des Flusskrebses Orconectes limosus: Reinigung und Charakterisierung. Z. Naturforsch. B (1968) 23, 1508-1511.', '3': 13583997})
        self.assertEqual(enzyme[0].params('MW')[0].comments, "#1# gel filtration <1>")
        self.assertEqual(enzyme[0].params('MW')[0].what, "molecular weight")

        self.assertEqual(enzyme[0].params('RE')[0].value, "D-glutamate + H2O + O2 = 2-oxoglutarate + NH3 + H2O2")
        self.assertEqual(enzyme[0].params('RE')[0].what, "reaction catalyzed")
        self.assertEqual(enzyme[0].params('RE')[0].comments, None)

        self.assertEqual(enzyme[0].params('RT')[0].value, "oxidation")
        self.assertEqual(enzyme[0].params('RT')[0].what, "reaction type")
        self.assertEqual(enzyme[0].params('RT')[0].comments, None)

        self.assertEqual(enzyme[0].params('RT')[1].value, "oxidative deamination")
        self.assertEqual(enzyme[0].params('RT')[1].what, "reaction type")
        self.assertEqual(enzyme[0].params('RT')[1].comments, None)

        self.assertEqual(enzyme[0].params('RT')[2].value, "redox reaction")
        self.assertEqual(enzyme[0].params('RT')[3].value, "reduction")
        self.assertEqual(enzyme[0].params('RT')[1000].value, None)

        self.assertEqual(enzyme[0].params('ST')[0].value, "cell culture")
        self.assertEqual(enzyme[0].params('ST')[0].get("bto"), "BTO_0000214")

        self.assertEqual(enzyme[0].params('UknownParam')[0].value, None)
        self.assertEqual(enzyme[0].params('UknownParam')[1000].value, None)

        enzyme = Enzyme.select().where(Enzyme.ec_number == '3.5.1.43')
        self.assertEqual(enzyme[0].organism, 'Bacillus circulans')

        Q = Enzyme.search_by_name("glutaminase")
        self.assertEqual(len(Q), 0)        
        Q = Enzyme.search_by_name("%glutaminase")
        self.assertEqual(len(Q), 1)
        self.assertEqual(Q[0].name, 'peptidyl-glutaminase')
        
        
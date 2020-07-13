import sys
import os
import unittest

from gws.prism.controller import Controller
from gws.settings import Settings
from biota.eco import ECO, ECOJSONStandardViewModel, ECOJSONPremiumViewModel

############################################################################################
#
#                                        TestECO
#                                         
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_path")


class TestECO(unittest.TestCase):
    @classmethod
    
    def setUpClass(cls):
        ECO.drop_table()
        ECO.create_table()
        pass
   
    @classmethod
    def tearDownClass(cls):
        #ECO.drop_table()
        pass
    
    def test_db_object(self):
        ### Test ECO class ###
        files = dict(
            eco_data = "eco.obo",
        )

        files_test = dict(
            eco_data = "eco_test.obo",
        )

        ECO.create_eco(test_data_path, **files_test)
        Controller.save_all()
        self.assertEqual(ECO.get(ECO.eco_id == 'ECO:0000001').name, "inference from background scientific knowledge")
        
        # --------- Testing views --------- #
        eco1 = ECO.get(ECO.eco_id == 'ECO:0000002')
        
        eco1_standard_view_model = ECOJSONStandardViewModel(eco1)
        eco1_premium_view_model = ECOJSONPremiumViewModel(eco1)

        view1 = eco1_standard_view_model.render()
        view2 = eco1_premium_view_model.render()

        self.assertEqual(view1,"""
            {
            "id": ECO:0000002,
            "name": direct assay evidence,
            }
        """)

        self.assertEqual(view2,"""
            {
            "id": ECO:0000002,
            "name": direct assay evidence,
            "ancestors": ['ECO:0000006']
            }
        """)
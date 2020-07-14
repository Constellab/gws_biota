import unittest

from gws.prism.controller import Controller
from gws.settings import Settings

from biota.enzymeAnnotation import EnzymeAnnotation, EnzymeAnnotationJSONStandardViewModel, EnzymeAnnotationJSONPremiumViewModel

############################################################################################
#
#                                        Test Enzyme Annotation
#                                         
############################################################################################
settings = Settings.retrieve()
test_data_path = settings.get_data("biota_test_data_dir")

class TestEnzymeAnnotation(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        EnzymeAnnotation.drop_table()
        EnzymeAnnotation.create_table()
   
    @classmethod
    def tearDownClass(cls):
        #EnzymeAnnotation.drop_table()
        pass
        

    def test_db_object(self):
        
        EnzymeAnnotation.create_annotation()
        self.assertEqual(EnzymeAnnotation.get(EnzymeAnnotation.go_term_id == 6176).reference, 'PMID:21873635')
        self.assertEqual(EnzymeAnnotation.get(EnzymeAnnotation.reference == "GO_REF:0000044").assigned_by, 'UniProt')

        # --------- Testing views --------- #
        enzyme_annotation1 = EnzymeAnnotation.get(EnzymeAnnotation.reference == 'GO_REF:0000044')
        
        standard_view_model = EnzymeAnnotationJSONStandardViewModel(enzyme_annotation1)
        premium_view_model = EnzymeAnnotationJSONPremiumViewModel(enzyme_annotation1)
        
        view1 = standard_view_model.render()
        view2 = premium_view_model.render()

        self.assertEqual(view1,"""
            {
            "gene product id": P38115,
            "GO term": GO:0005737,
            "ECO term": ECO:0000322,
            "reference": GO_REF:0000044,
            "taxonomy": None,
            "assigned by": UniProt
            }
        """)

        self.assertEqual(view2, """
            {
            "gene product id": P38115,
            "GO term": GO:0005737,
            "qualifier": part_of
            "GO aspect": C,
            "ECO term": ECO:0000322,
            "evidence code": IEA
            "reference": GO_REF:0000044,
            "taxonomy": None,
            "assigned by": UniProt
            }
        """)
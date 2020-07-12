import sys
import os
import unittest

from peewee import CharField, chunked
from gws.prism.model import Model, ViewModel,ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from starlette.testclient import TestClient

from biota.enzymeAnnotation import EnzymeAnnotation, EnzymeAnnotationJSONStandardViewModel, EnzymeAnnotationJSONPremiumViewModel
from manage import settings

############################################################################################
#
#                                        Test Enzyme Annotation
#                                         
############################################################################################

input_db_dir = settings.get_data("biota_db_path")


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
        files = dict(
            chebi_data = "chebi.obo",
        )

        files_test = dict(
            chebi_data = "chebi_test.obo",
        )
        
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
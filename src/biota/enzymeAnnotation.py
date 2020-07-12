import sys
import os
import unittest

from biota.annotation import Annotation
from biota.go import GO
from biota.eco import ECO
from biota.enzyme import Enzyme
from biota.taxonomy import Taxonomy
from annotation.annotation import QuickGOAnnotation
from biota.annotation import Annotation
from gws.prism.app import App
from gws.prism.view import HTMLViewTemplate, JSONViewTemplate, PlainTextViewTemplate
from gws.prism.model import Model, ViewModel, ResourceViewModel, Resource, DbManager
from gws.prism.controller import Controller
from peewee import IntegerField, DateField, DateTimeField, CharField, ForeignKeyField

####################################################################################
#
# Annotation class
#
####################################################################################

class EnzymeAnnotation(Annotation):
    gene_product_id = CharField(null=True, index=True)
    ec_id = CharField(null=True, index=True)
    go_term = ForeignKeyField(GO, backref='go_associated', null = True)
    evidence = ForeignKeyField(ECO, backref='eco_associated', null = True)
    reference = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Taxonomy, backref='taxonomy_associated', null = True)
    assigned_by = CharField(null=True, index=True)
    
    class Meta():
        table_name = 'enzyme_annotations'

    #Setters
    def set_gene_product_id(self, gene):
        self.gene_product_id = gene
    
    def set_ec_id(self, ec):
        self.gene_ec_id = ec
    
    def set_reference(self, ref):
        self.reference = ref

    def set_assigned_by(self, assignment):
        self.assigned_by = assignment

    def set_go_term(self):
        if('go term' in self.data.keys()):
            try:
                go_reference = GO.get(GO.go_id == self.data['go term'])
                self.go_term = go_reference
            except:
                print("could not find the go term: " + str(self.data['go term']))

    def set_evidence(self):
        if('eco id' in self.data.keys()):
            try:
                eco_reference = ECO.get(ECO.eco_id == self.data['eco id'])
                self.evidence = eco_reference
            except:
                print("could not find the eco term: " + str(self.data['eco id']))

    def set_taxonomy(self):
        if('taxon id' in self.data.keys()):
            try:
                taxonomy_reference = Taxonomy.get(Taxonomy.tax_id == self.data['taxon id'])
                self.taxonomy = taxonomy_reference
            except:
                print("could not find the taxonomy term: " + str(self.data['taxon id']))

    #Inserts
    def insert_gene_product_id(list__, key):
        for element in list__:
            element.set_gene_product_id(element.data[key])
    
    def insert_ec_id(list__, key):
        for element in list__:
            element.set_ec_id(element.data[key])

    def insert_reference(list__, key):
        for element in list__:
            element.set_reference(element.data[key])
    
    def insert_assignment(list__, key):
        for element in list__:
            element.set_assigned_by(element.data[key])
    
    @classmethod
    def create_annotation(cls):
        list_annotation = []
        q = Enzyme.select().where(Enzyme.data['uniprot'] != 'null')
        for enzyme in q:
            list_ann = QuickGOAnnotation.get_tsv_file_from_uniprot_id(str(enzyme.uniprot_id))
            for element in list_ann:
                list_annotation.append(element)
        annnotations = [cls(data = d) for d in list_annotation]
        cls.insert_gene_product_id(annnotations, 'gene product id')
        cls.insert_reference(annnotations, 'reference')
        cls.insert_assignment(annnotations, 'assigned by')
        Controller.save_all()
        for annotation in annnotations:
            annotation.set_go_term()
            annotation.set_evidence()
        Controller.save_all()

class EnzymeAnnotationJSONStandardViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "gene product id": {{view_model.model.gene_product_id}},
            "GO term": {{view_model.model.go_term.go_id}},
            "ECO term": {{view_model.model.evidence.eco_id}},
            "reference": {{view_model.model.reference}},
            "taxonomy": {{view_model.model.taxonomy}},
            "assigned by": {{view_model.model.assigned_by}}
            }
        """)

class EnzymeAnnotationJSONPremiumViewModel(ResourceViewModel):
    template = JSONViewTemplate("""
            {
            "gene product id": {{view_model.model.gene_product_id}},
            "GO term": {{view_model.model.go_term.go_id}},
            "qualifier": {{view_model.model.data['qualifier']}}
            "GO aspect": {{view_model.model.data['go aspect']}},
            "ECO term": {{view_model.model.evidence.eco_id}},
            "evidence code": {{view_model.model.data['go evidence code']}}
            "reference": {{view_model.model.reference}},
            "taxonomy": {{view_model.model.taxonomy}},
            "assigned by": {{view_model.model.assigned_by}}
            }
        """)
from gws.prism.model import ResourceViewModel
from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate

from biota.annotation import Annotation
from biota.go import GO
from biota.eco import ECO
from biota.enzyme import Enzyme
from biota.taxonomy import Taxonomy
from quickgo.quickgo import QuickGOAnnotation
from peewee import CharField, ForeignKeyField
import time

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
    _table_name = 'enzyme_annotation'

    # setters
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

    # inserts
    @classmethod
    def insert_gene_product_id(cls, list__, key):
        for element in list__:
            element.set_gene_product_id(element.data[key])
    
    @classmethod
    def insert_ec_id(cls, list__, key):
        for element in list__:
            element.set_ec_id(element.data[key])

    @classmethod
    def insert_reference(cls, list__, key):
        for element in list__:
            element.set_reference(element.data[key])
    
    @classmethod
    def insert_assignment(cls, list__, key):
        for element in list__:
            element.set_assigned_by(element.data[key])
    
    @classmethod
    def create_annotation(cls):
        list_annotation = []
        q = Enzyme.select().where(Enzyme.data['uniprot'] != 'null')
        list_q = list(q)
        start = 0
        stop = 0
        size_select = len(q)
        bulk_size = 50
        while True:
            print("Trying to record 50 items from quickgo...")
            if start >= size_select-1:
                break
            
            stop = min(start+bulk_size, size_select-1)

            elems = list_q[start:(stop+1)]

            if len(elems) == 0:
                    return None

            for enzyme in elems:
                start_time = time.time()
                list_ann = QuickGOAnnotation.get_tsv_file_from_uniprot_id(str(enzyme.uniprot_id))
                try:
                    for element in list_ann:
                        list_annotation.append(element)
                    print('Results for ' + enzyme.uniprot_id + ' have been collected successfully')
                except:
                    print('list empty')
            
            annotations = [cls(data = d) for d in list_annotation]

            cls.insert_gene_product_id(annotations, 'gene product id')
            cls.insert_reference(annotations, 'reference')
            cls.insert_assignment(annotations, 'assigned by')
            cls.save_all()
            
            elapsed_time = time.time() - start_time
            print("Loading 50 items from quickgo extract from QuickGO in: time = {}".format(elapsed_time/60))

            start = stop
        
        start_time = time.time()
        for annotation in EnzymeAnnotation.select():
            annotation.set_go_term()
            annotation.set_evidence()
        
        cls.save_all()
        elapsed_time = time.time() - start_time
        print("Get GO and ECO id for all table in: time = {}".format(elapsed_time/60))

    class Meta():
        table_name = 'enzyme_annotation'

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
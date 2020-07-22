from gws.prism.model import ResourceViewModel
from gws.prism.controller import Controller
from gws.prism.view import JSONViewTemplate

from biota.prism.annotation import Annotation
from biota.prism.go import GO
from biota.prism.eco import ECO
from biota.prism.enzyme import Enzyme
from biota.prism.taxonomy import Taxonomy
from biota.helper.quickgo import QuickGOAnnotation
from peewee import CharField, ForeignKeyField
#import time

####################################################################################
#
# Annotation class
#
####################################################################################

class EnzymeAnnotation(Annotation):
    """

    This class allows to load Enzyme Gene Annotation extract from QuickGO browser 
    website in the database
    Through this class, the user has acess to all the annotations about an enzyme
    if this one has a uniprot id referenced

    
    GO entities are automatically created by the create_annotation() method

    :type gene_product_id: CharField 
    :property gene_product_id: uniprot id of the concerned protein
    :type ec_id: sts 
    :property ec_id: ec number of the protein
    :type go_term: GO
    :property go_term: GO identifier in the GO table
    :type evidence: ECO
    :property evidence: ECO identifier in the ECO table
    :type reference: str
    :property reference: reference number of the annotation (PMID, GO_REF, etc...)
    :type taxonomy: Taxonomy
    :property taxonomy: taxonomy identifier in the taxonomy database
    :type assigned_by: str
    :property assigned_by: database which created the annontation

    """
    gene_product_id = CharField(null=True, index=True)
    ec_id = CharField(null=True, index=True)
    go_term = ForeignKeyField(GO, backref='go_associated', null = True)
    evidence = ForeignKeyField(ECO, backref='eco_associated', null = True)
    reference = CharField(null=True, index=True)
    taxonomy = ForeignKeyField(Taxonomy, backref='taxonomy_associated', null = True)
    assigned_by = CharField(null=True, index=True)
    _table_name = 'enzyme_annotation'

    # -- C --

    @classmethod
    def create_annotation(cls):
        """
        Creates and registers EnzymeAnnotation entities in the database
        Use the quickgo helper module of biota to get all annotation in a list
        Creates annotations
        Register compounds by calling the save_all() method 

        """
        list_annotation = []
        page_number = 1
        items_per_page = 100
        while True:
            list_q = Enzyme.select().where(Enzyme.data['uniprot'] != 'null').paginate(page_number, items_per_page)

            if len(list_q) == 0:
                break

            for enzyme in list_q:
                #start_time = time.time()
                list_ann = QuickGOAnnotation.get_tsv_file_from_uniprot_id(str(enzyme.uniprot_id))
                try:
                    for element in list_ann:
                        list_annotation.append(element)
                    #print('Results for ' + enzyme.uniprot_id + ' have been collected successfully')
                except:
                    pass
                    #print('list empty')
            
            annotations = [cls(data = d) for d in list_annotation]

            for annotation in annotations:
                annotation.set_gene_product_id(annotation.data['gene product id'])
                annotation.set_reference(annotation.data['reference'])
                annotation.set_assigned_by(annotation.data['assigned by'])

            cls.save_all(annotations)
            page_number = page_number + 1
            #elapsed_time = time.time() - start_time
            #print("Loading 50 items from quickgo extract from QuickGO in: time = {}".format(elapsed_time/60))

            
        
        #start_time = time.time()
        for annotation in EnzymeAnnotation.select():
            annotation.set_go_term()
            annotation.set_evidence()
        
        cls.save_all(annotations)
        #elapsed_time = time.time() - start_time
        #print("Get GO and ECO id for all table in: time = {}".format(elapsed_time/60))

    # -- S --

    def set_gene_product_id(self, gene):
        self.gene_product_id = gene
    
    def set_ec_id(self, ec):
        self.gene_ec_id = ec
    
    def set_reference(self, ref):
        self.reference = ref

    def set_assigned_by(self, assignment):
        self.assigned_by = assignment

    def set_go_term(self):
        """

        Collects the GO identifier of the annotation in the go table and update 
        the go_id property of the annotation

        """
        if('go term' in self.data.keys()):
            try:
                go_reference = GO.get(GO.go_id == self.data['go term'])
                self.go_term = go_reference
            except:
                pass
                #print("could not find the go term: " + str(self.data['go term']))

    def set_evidence(self):
        """
        
        Collects the ECO identifier of the annotation in the eco table and update 
        the eco_id property of the annotation

        """
        if('eco id' in self.data.keys()):
            try:
                eco_reference = ECO.get(ECO.eco_id == self.data['eco id'])
                self.evidence = eco_reference
            except:
                pass
                #print("could not find the eco term: " + str(self.data['eco id']))

    def set_taxonomy(self):
        """
        
        Collects the Taxonomy identifier of the annotation in the taxonomy table and update 
        the taxonomy property of the annotation

        """
        
        if('taxon id' in self.data.keys()):
            try:
                taxonomy_reference = Taxonomy.get(Taxonomy.tax_id == self.data['taxon id'])
                self.taxonomy = taxonomy_reference
            except:
                pass
                #print("could not find the taxonomy term: " + str(self.data['taxon id']))

    
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
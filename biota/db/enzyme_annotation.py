# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


from peewee import CharField, ForeignKeyField

from gws.prism.model import Resource
from gws.prism.controller import Controller

from biota.db.go import GO
from biota.db.eco import ECO
from biota.db.enzyme_function import EnzymeFunction
from biota.db.taxonomy import Taxonomy

class EnzymeAnnotation(Resource):
    """
    This class represents Enzyme Gene Annotation extracted from QuickGO.
    
    QuickGO provides a unified interface to query information about ontology terms 
    from GO (the Gene Ontology) and ECO (the Evidence & Conclusion Ontology), 
    Gene Ontology annotations from the EBI's GOA database, and gene products 
    (proteins from UniProt, RNA from RNAcentral and complexes from ComplexPortal) (https://www.ebi.ac.uk/QuickGO).
    QuickGo is available under the APACHE LICENSE, VERSION 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
     
    :property gene_product_id: uniprot id of the concerned protein
    :type gene_product_id: CharField 
    :property ec_id: ec number of the protein
    :type ec_id: sts 
    :property go_term: GO identifier in the GO table
    :type go_term: GO
    :property evidence: ECO identifier in the ECO table
    :type evidence: ECO
    :property reference: reference number of the annotation (PMID, GO_REF, etc...)
    :type reference: str
    :property taxonomy: taxonomy identifier in the taxonomy database
    :type taxonomy: Taxonomy
    :property assigned_by: database which created the annontation
    :type assigned_by: str
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
    def create_annotation_db(cls):
        """
        Creates and fills the `enzyme_annotation` database 
        """

        from biota._helper.quickgo import QuickGOAnnotation

        list_annotation = []
        page_number = 1
        items_per_page = 100
        while True:
            list_q = EnzymeFunction.select().where(EnzymeFunction.data['uniprot'] != 'null').paginate(page_number, items_per_page)

            if len(list_q) == 0:
                break

            for enzyme in list_q:
                list_ann = QuickGOAnnotation.get_tsv_file_from_uniprot_id(str(enzyme.uniprot_id))
                try:
                    for element in list_ann:
                        list_annotation.append(element)
                except:
                    pass
            
            annotations = [cls(data = d) for d in list_annotation]

            for annotation in annotations:
                annotation.set_gene_product_id(annotation.data['gene product id'])
                annotation.set_reference(annotation.data['reference'])
                annotation.set_assigned_by(annotation.data['assigned by'])

            cls.save_all(annotations)
            page_number = page_number + 1
                
        for annotation in EnzymeAnnotation.select():
            annotation.set_go_term()
            annotation.set_evidence()
        
        cls.save_all(annotations)

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

        if 'go term' in self.data.keys():
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

        if 'eco id' in self.data.keys():
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
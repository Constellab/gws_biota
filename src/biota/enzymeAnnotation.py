from biota.annotation import Annotation
from biota.go import GO
from biota.eco import ECO
from biota.taxonomy import Taxonomy
from peewee import CharField, ForeignKeyField

####################################################################################
#
# Annotation class
#
####################################################################################

class EnzymeAnnotation(Annotation):
    gene_id = CharField(null=True, index=True)
    go_term = ForeignKeyField('GO', backref='go_associated', null = True)
    evidence = ForeignKeyField('ECO', backref='eco_associated', null = True)
    reference = CharField(null=True, index=True)
    taxonomy = ForeignKeyField('Taxonomy', backref='taxonomy_associated', null = True)
    assigned_by = CharField(null=True, index=True)
    _table_name = 'enzyme_annotations'

    #Setters
    def set_gene_id(self, gene):
        self.gene_id = gene
    
    def set_reference(self, ref):
        self.reference = ref

    def set_assigned_by(self, assignment):
        self.assigned_by = assignment

    class Meta():
        table_name = 'enzyme_annotations'
    
    #Inserts
    @classmethod
    def insert_gene_id(cls, list__, key):
        for annotations in list__:
            annotations.set_gene_id(annotations.data[key])

    @classmethod
    def insert_reference(cls, list__, key):
        for annotations in list__:
            annotations.set_reference(annotations.data[key])
    
    @classmethod
    def insert_assignment(cls, list__, key):
        for annotations in list__:
            annotations.set_assigned_by(annotations.data[key])
    
    @classmethod
    def create_annotation(cls, input_db_dir, **files):
        #onto = Chebi.create_ontology_from_file(input_db_dir, files['chebi_data'])
        list_annotation = #Chebi.parse_onto_from_ontology(onto)
        annotations = [cls(data = dict_) for dict_ in list_annotation]
        cls.insert_gene_id(chebis, "id")
        cls.insert_reference(chebis, "name")
        #cls.insert_assignment(chebis, "id")
        return(list_annotation)

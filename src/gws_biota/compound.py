# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com
#
# ChEBI Copyright Notice and License:
# ChEBI data are available under the Creative Commons License (CC BY 4.0).
# The Creative Commons Attribution License CC BY 4.0 
# is applied to all copyrightable parts of BRENDA. 
# The copyrightable parts of BRENDA are copyright-protected by Prof. Dr. D. Schomburg, Technische 
# Universität Braunschweig, BRICS,Department of Bioinformatics and Biochemistry, 
# Rebenring 56, 38106 Braunschweig, Germany.
# https://www.brenda-enzymes.org
#
# Attribution 4.0 International (CC BY 4.0) information, 2020:
# You are free to:
# * Share — copy and redistribute the material in any medium or format
# * Adapt — remix, transform, and build upon the material
#     for any purpose, even commercially.
# This license is acceptable for Free Cultural Works.
# The licensor cannot revoke these freedoms as long as you follow the license terms.
# https://creativecommons.org/licenses/by/4.0/.

from peewee import CharField, FloatField, IntegerField, ForeignKeyField
from peewee import Model as PeeweeModel

from gws_core import BadRequestException, ResourceDecorator
from .base import Base, DbManager

@ResourceDecorator("Compound")
class Compound(Base):
    """
    This class represents ChEBI Ontology terms.

    Chemical Entities of Biological Interest (ChEBI) includes an ontological classification, whereby the 
    relationships between molecular entities or classes of entities and their parents and/or children are 
    specified (https://www.ebi.ac.uk/chebi/). ChEBI data are available under the Creative Commons License (CC BY 4.0),
    https://creativecommons.org/licenses/by/4.0/


    :property chebi_id: id of the ChEBI term
    :type chebi_id: class:`peewee.CharField`
    """

    chebi_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    metacyc_id = CharField(null=True, index=True)
    formula = CharField(null=True, index=True)
    charge = FloatField(null=True, index=True)
    mass = FloatField(null=True, index=True)
    monoisotopic_mass = FloatField(null=True, index=True)
    inchi = CharField(null=True, index=True)
    inchikey = CharField(null=True, index=True)
    smiles = CharField(null=True, index=True)
    chebi_star = CharField(null=True, index=True)

    _ancestors = None
    _table_name = 'biota_compound'
    
    # -- A --

    @property
    def ancestors(self):
        if not self._ancestors is None:
            return self._ancestors

        self._ancestors = []
        Q = CompoundAncestor.select().where(CompoundAncestor.compound == self.id)
        for q in Q:
            self._ancestors.append(q.ancestor)
        
        return self._ancestors

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `Compound` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        CompoundAncestor.create_table()
        
    @classmethod
    def create_compound_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `chebi_ontology` database

        :type biodata_dir: str
        :param biodata_dir: path of the :file:`chebi.obo`
        :type kwargs: dict
        :param kwargs: dictionnary that contains all data files names
        :returns: None
        :rtype: None
        """

        from ._helper.chebi import Chebi as ChebiHelper

        data_dir, corrected_file_name = ChebiHelper.correction_of_chebi_file(biodata_dir, kwargs['chebi_file'])

        onto = ChebiHelper.create_ontology_from_file(data_dir, corrected_file_name)
        list_chebi = ChebiHelper.parse_onto_from_ontology(onto)
        compounds = [cls(data = dict_) for dict_ in list_chebi]
        job = kwargs.get('job',None)
        
        for comp in compounds:
            comp.set_name(comp.data["name"])
            comp.chebi_id = comp.data["id"]
            comp.formula = comp.data["formula"]
            comp.inchi = comp.data["inchi"]
            comp.inchikey = comp.data["inchikey"]
            comp.smiles = comp.data["smiles"]

            if not comp.data["mass"] is None:
                comp.mass = float(comp.data["mass"])
            
            if not comp.data["monoisotopic_mass"] is None:
                comp.monoisotopic_mass = float(comp.data["monoisotopic_mass"])
            
            if not comp.data["charge"] is None:
                comp.charge = float(comp.data["charge"])
                
            comp.chebi_star = comp.data["subsets"]
            
            if "kegg" in comp.data["xref"]:
                comp.kegg_id = comp.data["xref"]["kegg"]
                del comp.data["xref"]["kegg"]

            if "metacyc" in comp.data["xref"]:
                comp.metacyc_id = comp.data["xref"]["metacyc"]
                del comp.data["xref"]["metacyc"]

            del comp.data["id"]
            del comp.data["inchi"]
            del comp.data["formula"]
            del comp.data["inchikey"]
            del comp.data["smiles"]
            del comp.data["mass"]
            del comp.data["monoisotopic_mass"]
            del comp.data["charge"]
            del comp.data["subsets"]

            if not job is None:
                comp._set_job(job)

        cls.save_all(compounds)
        
        # save ancestors
        vals = []
        bulk_size = 100
        with DbManager.db.atomic() as transaction:
            try:
                for compound in compounds:
                    if 'ancestors' in compound.data.keys():
                        val = compound._get_ancestors_query()
                        if len(val) != 0:
                            for v in val:
                                vals.append(v)
                                if len(vals) == bulk_size:
                                    CompoundAncestor.insert_many(vals).execute()
                                    vals = []
                            
                            if len(vals) != 0:
                                CompoundAncestor.insert_many(vals).execute()
                                vals = []
                
            except:
                raise BadRequestException("Cannot save all chebi ancestors")
    
    @classmethod
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `Compound` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        CompoundAncestor.drop_table()
        super().drop_table(*arg, **kwargs)
        
    # -- G --

    def _get_ancestors_query(self):
        """
        Look for the compound term ancestors and returns all ancetors relations in a list 

        :returns: a list of dictionnaries inf the following format: {'compound': self.id, 'ancestor': ancestor.id}
        :rtype: list
        """
        vals = []
        for i in range(0, len(self.data['ancestors'])):
            if(self.data['ancestors'][i] != self.chebi_id):
                val = {'compound': self.id, 'ancestor': Compound.get(Compound.chebi_id == self.data['ancestors'][i]).id }
                vals.append(val)
        return(vals)
    
    # -- P --
    
    @property
    def pathways(self):
        from .pathway import PathwayCompounds
        try:
            pcomps = PathwayCompounds.select().where(PathwayCompounds.chebi_id == self.chebi_id)
            pathways = []
            for pc in pcomps:
                pw = pc.pathway
                if pw:
                    pathways.append(pc.pathway)
            
            return pathways
        except:
            return None
    
    # -- R --
    
    @property
    def reactions(self):
        from .reaction import ReactionSubstrate, ReactionProduct
        rxns = []
        Q = ReactionSubstrate.select().where(ReactionSubstrate.compound == self)
        for r in Q:
            rxns.append(r.reaction)
            
        Q = ReactionProduct.select().where(ReactionProduct.compound == self)
        for r in Q:
            rxns.append(r.reaction)
            
        return rxns
    
class CompoundAncestor(PeeweeModel):
    """
    This class defines the many-to-many relationship between the compound terms and theirs ancestors

    :type compound: CharField 
    :property compound: id of the concerned compound term
    :type ancestor: CharField 
    :property ancestor: ancestor of the concerned compound term
    """
    
    compound = ForeignKeyField(Compound)
    ancestor = ForeignKeyField(Compound)
    
    class Meta:
        table_name = 'biota_compound_ancestors'
        database = DbManager.db
        indexes = (
            (('compound', 'ancestor'), True),
        )
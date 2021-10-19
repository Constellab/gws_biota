# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField, ForeignKeyField, ManyToManyField, DeferredThroughModel, TextField
from peewee import Model as PeeweeModel

from gws_core.model.typing_register_decorator import typing_registrator
from ..base.base import Base
from ..db.db_manager import DbManager
from ..compound.compound import Compound
from ..enzyme.enzyme import Enzyme


####################################################################################
#
# Reaction class
#
####################################################################################

ReactionSubstrateDeferred = DeferredThroughModel()
ReactionProductDeferred = DeferredThroughModel()
ReactionEnzymeDeferred = DeferredThroughModel()

@typing_registrator(unique_name="Reaction", object_type="MODEL", hide=True)
class Reaction(Base):
    """
    This class represents metabolic reactions extracted from Rhea database.

    Rhea is an expert curated resource of biochemical reactions designed for the 
    annotation of enzymes and genome-scale metabolic networks and models (https://www.rhea-db.org/).
    Rhea data are available under the Creative 
    Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.

    :property rhea_id: rhea accession number
    :type rhea_id: CharField
    :property master_id: master id of the reaction
    :type master_id: CharField
    :property direction: direction of the reaction 
    :type direction: CharField (UN = undirected, LR = left-right, RL = right-left, BI = bidirectionnal)
    :property biocyc_ids: reaction identifier in the biocyc database
    :type biocyc_ids: CharField
    :property kegg_id: reaction identifier in the kegg databse
    :type kegg_id: CharField
    :property substrates: substrates of the reaction
    :type substrates: List of `Compound`
    :property products: products of the reaction
    :type products: List of `Compound`
    :property enzymes: enzymes of the reaction
    :type enzymes: List of `Enzyme`
    """
    rhea_id = CharField(null=True, index=True)
    master_id = CharField(null=True, index=True)
    direction = CharField(null=True, index=True)
    biocyc_ids = CharField(null=True, index=True)
    #brenda_id = CharField(null=True, index=True)
    metacyc_id = CharField(null=True, index=True)
    kegg_id = CharField(null=True, index=True)
    sabio_rk_id = CharField(null=True, index=True)
    substrates = ManyToManyField(Compound, through_model = ReactionSubstrateDeferred)
    products = ManyToManyField(Compound, through_model = ReactionProductDeferred)
    enzymes = ManyToManyField(Enzyme, through_model = ReactionEnzymeDeferred)

    ft_names = TextField(null=True, index=False)
    _default_full_text_column = "ft_names"
    _table_name = 'biota_reaction'

    # -- A --

    def append_biocyc_id(self, id):
        """
        Appends a biocyc id to the reaction

        :param id: The id
        :type id: str
        """
        try:
            self.biocyc_ids.append(id)
        except:
            self.biocyc_ids = []
            self.biocyc_ids.append(id)

    # -- C --

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `reaction` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.create_table`
        """
        super().create_table(*args, **kwargs)
        ReactionSubstrate.create_table()
        ReactionProduct.create_table()
        ReactionEnzyme.create_table()

    # -- D -- 

    @property
    def definition(self):
        return self.data["definition"]

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops `reaction` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        ReactionSubstrate.drop_table()
        ReactionProduct.drop_table()
        ReactionEnzyme.drop_table()
        super().drop_table(*args, **kwargs)

    # -- G --

    def get_title(self, default=None):
        return self.definition

    # -- I -- 

    def is_charge_balanced(self):
        total_substrate_charge = 0
        total_product_charge = 0
        for s in self.substrates:
            total_substrate_charge = total_substrate_charge + s.charge
        for p in self.products:
            total_product_charge = total_product_charge + p.charge
        return total_substrate_charge == total_product_charge

    def is_mass_balanced(self):
        total_substrate_mass = 0
        total_product_mass = 0
        for s in self.substrates:
            total_substrate_mass = total_substrate_mass + s.mass
        for p in self.products:
            total_product_mass = total_product_mass + p.mass
        return total_substrate_mass == total_product_mass

    # -- L --

    @property
    def position(self):
        from .reaction_position import ReactionPosition
        try:
            return ReactionPosition.get(ReactionPosition.rhea_id == self.rhea_id)
        except:
            return None
    # -- S -- 

    def set_direction(self, direction):
        """
        Set the direction of the reaction

        :param direction: The direction
        :type direction: str
        """
        self.direction = direction
            
    def set_kegg_id(self, kegg_id):
        """
        Set the KEGG id the reaction

        :param kegg_id: The kegg id
        :type kegg_id: str
        """
        self.kegg_id = kegg_id
    
    def set_rhea_id(self, kegg_id):
        """
        Set the RHEA id the reaction

        :param rhea_id: The RHEA id
        :type rhea_id: str
        """
        self.kegg_id = kegg_id

    def set_master_id(self, master_id):
        """
        Set the master id the reaction

        :param master_id: The master id
        :type master_id: str
        """
        self.master_id = master_id


class ReactionSubstrate(PeeweeModel):
    """
    This class defines the many-to-many relationship between susbtrates and reactions.

    :type compound: Compound 
    :property compound: subtrate of the reaction
    :type reaction: Reaction 
    :property reaction: concerned reaction
    """
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    
    class Meta:
        table_name = 'biota_reaction_substrates'
        database = DbManager.db


class ReactionProduct(PeeweeModel):
    """
    This class defines the many-to-many relationship between products and reactions.

    :property compound: product of the reaction
    :type compound: Compound 
    :property reaction: concerned reaction 
    :type reaction: Reaction 
    """
    compound = ForeignKeyField(Compound)
    reaction = ForeignKeyField(Reaction)
    
    class Meta:
        table_name = 'biota_reaction_products'
        database = DbManager.db

class ReactionEnzyme(PeeweeModel):
    """
    This class defines the many-to-many relationship between enzymes and reactions.

    :property enzyme: enzyme of the reaction
    :type enzyme: Enzyme 
    
    :property reaction: concerned reaction
    :type reaction: Reaction 
    """
    enzyme = ForeignKeyField(Enzyme)
    reaction = ForeignKeyField(Reaction)
    
    class Meta:
        table_name = 'biota_reaction_enzymes'
        database = DbManager.db

ReactionSubstrateDeferred.set_model(ReactionSubstrate)
ReactionProductDeferred.set_model(ReactionProduct)
ReactionEnzymeDeferred.set_model(ReactionEnzyme)

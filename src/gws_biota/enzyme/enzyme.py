# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from collections import OrderedDict

from gws_core import BadRequestException
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import (CharField, DeferredThroughModel, ForeignKeyField,
                    ManyToManyField, ModelSelect, TextField)
from playhouse.mysql_ext import Match

from ..base.base import Base
from ..base.simple_base_model import SimpleBaseModel
from ..bto.bto import BTO
from ..db.db_manager import DbManager
from ..protein.protein import Protein
from ..taxonomy.taxonomy import Taxonomy
from .deprecated_enzyme import DeprecatedEnzyme
from .enzyme_class import EnzymeClass
from .enzyme_ortholog import EnzymeOrtholog
from .enzyme_param import Params
from .enzyme_pathway import EnzymePathway

EnzymeBTODeffered = DeferredThroughModel()


@typing_registrator(unique_name="Enzyme", object_type="MODEL", hide=True)
class Enzyme(Base):
    """
    This class represents enzymes extracted from open databases.

    :property go_id: GO term id
    :type go_id: str
    :property name: name of the compound
    :type name: str
    :property ec: ec accession number
    :type ec: str
    :property taxonomy: taxonomy id that gives the organism
    :type taxonomy: str
    :property bto: bto id that gives the tissue location
    :type bto: class:biota.BTO
    :property uniprot_id: uniprot id of the enzyme
    :type uniprot_id: str

    * Uniprot:
        The Universal Protein Resource (UniProt) is a comprehensive resource for protein sequence and annotation data.
        The UniProt databases are the UniProt Knowledgebase (UniProtKB), the UniProt Reference Clusters (UniRef),
        and the UniProt Archive (UniParc). The UniProt consortium and host institutions EMBL-EBI, SIB and PIR are
        committed to the long-term preservation of the UniProt databases.
    * Brenda:
        BRENDA is the main collection of enzyme functional data available to the scientific community
        (https://www.brenda-enzymes.org/). BRENDA data are available under the Creative
        Commons License (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
    * BKMS:
        BKMS-react is an integrated and non-redundant biochemical reaction database
        containing known enzyme-catalyzed and spontaneous reactions.
        Biochemical reactions collected from BRENDA, KEGG, MetaCyc and
        SABIO-RK were matched and integrated by aligning substrates and products.
    """

    ec_number = CharField(null=True, index=True)
    uniprot_id = CharField(null=True, index=True)
    tax_superkingdom = CharField(null=True, index=True)
    tax_clade = CharField(null=True, index=True)
    tax_kingdom = CharField(null=True, index=True)
    tax_subkingdom = CharField(null=True, index=True)
    tax_class = CharField(null=True, index=True)
    tax_phylum = CharField(null=True, index=True)
    tax_subphylum = CharField(null=True, index=True)
    tax_order = CharField(null=True, index=True)
    tax_genus = CharField(null=True, index=True)
    tax_family = CharField(null=True, index=True)
    tax_species = CharField(null=True, index=True)
    tax_id = CharField(null=True, index=True)
    related_deprecated_enzyme = None  # dyamically added if by method select_and_follow_if_deprecated
    bto = ManyToManyField(BTO, through_model=EnzymeBTODeffered)

    ft_names = TextField(null=True, index=True)
    _table_name = 'biota_enzymes'

    # -- A --

    def as_json(self, jsonifiable_data_keys: list = ['name', 'description'], **kwargs):

        return super().as_json(
            jsonifiable_data_keys=jsonifiable_data_keys,
            **kwargs
        )

    @classmethod
    def create_table(cls, *args, **kwargs):
        """
        Creates `enzyme` table and related tables.

        Extra parameters are passed to :meth:`create_table`
        """

        EnzymeClass.create_table()
        DeprecatedEnzyme.create_table()
        EnzymePathway.create_table()
        EnzymeOrtholog.create_table()
        super().create_table(*args, **kwargs)
        EnzymeBTO.create_table()

    @property
    def classification(self):
        ec_class = ".".join(self.ec_number.split(".")[0:-1]) + ".-"
        return EnzymeClass.get(EnzymeClass.ec_number == ec_class)

    # -- D --

    @classmethod
    def drop_table(cls, *args, **kwargs):
        """
        Drops `enzyme` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """

        EnzymeClass.drop_table()
        EnzymeOrtholog.drop_table()
        EnzymePathway.drop_table(*args, **kwargs)
        EnzymeBTO.drop_table(*args, **kwargs)
        DeprecatedEnzyme.drop_table(*args, **kwargs)
        super().drop_table(*args, **kwargs)

    # -- F --

    @property
    def protein(self):
        try:
            return Protein.get(Protein.uniprot_id == self.uniprot_id)
        except:
            return None

    # -- N --

    @property
    def synomyms(self):
        """
        Name of the enzyme orthologue

        :returns: The name of the enzyme orthologue
        :rtype: str
        """

        return ",".join([sn.capitalize() for sn in self.data.get("SN", [''])])

    # -- O --

    @property
    def organism(self):
        """
        Name of the organism

        :returns: The name of the organism associated to the enzyme function
        :rtype: str
        """
        return self.data["organism"].capitalize()

    # -- P --

    @property
    def pathway(self):
        try:
            return EnzymePathway.get(EnzymePathway.ec_number == self.ec_number)
        except:
            return None

    def params(self, name) -> Params:
        """
        Returns the list of parameters associated with `name`

        :param name: Name of the parameter
        :type name: str
        :returns: Parameters
        :rtype: ParamList
        """

        return Params(name, self.data)

    # -- R --

    @property
    def reactions(self):
        """
        Returns the list of reactions associated with the enzyme function
        :returns: List of reactions
        :rtype: Query rows
        """

        from ..reaction.reaction import Reaction, ReactionEnzyme
        Q = Reaction.select() \
                    .join(ReactionEnzyme) \
                    .where(ReactionEnzyme.enzyme == self)
        return Q

    # -- S --

    @classmethod
    def select_and_follow_if_deprecated(self, ec_number, tax_id=None):
        if tax_id:
            try:
                tax = Taxonomy.get(Taxonomy.tax_id == tax_id)
            except:
                raise BadRequestException(f"Taxonomy ID {tax_id} not found")

            tax_field = getattr(Enzyme, "tax_"+tax.rank)
            Q = Enzyme.select().where((Enzyme.ec_number == ec_number) & (tax_field == tax_id))
        else:
            Q = Enzyme.select().where(Enzyme.ec_number == ec_number)

        if not len(Q):
            Q = []
            depre_Q = DeprecatedEnzyme.select().where(DeprecatedEnzyme.ec_number == ec_number)

            for deprecated_enzyme in depre_Q:
                Q_selected = deprecated_enzyme.select_new_enzymes()
                for new_enzyme in Q_selected:
                    if tax_id:

                        if getattr(new_enzyme, "tax_"+tax.rank) == tax_id:
                            new_enzyme.related_deprecated_enzyme = deprecated_enzyme
                            Q.append(new_enzyme)
                    else:
                        new_enzyme.related_deprecated_enzyme = deprecated_enzyme
                        Q.append(new_enzyme)

        return Q

    def save(self, *arg, **kwargs):
        if isinstance(self.data, OrderedDict):
            self.data = dict(self.data)
        return super().save(*arg, **kwargs)

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['ft_names'], 'I_F_BIOTA_ENZ')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.ft_names), phrase, modifier=modifier))

    # -- T --

    @property
    def taxonomy(self):
        try:
            return Taxonomy.get(Taxonomy.tax_id == self.tax_id)
        except:
            return None

    # -- U --


class EnzymeBTO(SimpleBaseModel):
    """
    This class refers to tissues of brenda enzymes
    EnzymeBTO entities are created by the __update_tissues() method of the Enzyme class

    :type enzyme: Enzyme
    :property enzyme: id of the concerned enzyme
    :type bto: BTO
    :property bto: tissue location
    """

    enzyme = ForeignKeyField(Enzyme)
    bto = ForeignKeyField(BTO)

    class Meta:
        table_name = 'biota_enzyme_btos'
        database = DbManager.db


# Resolve dependencies.
EnzymeBTODeffered.set_model(EnzymeBTO)

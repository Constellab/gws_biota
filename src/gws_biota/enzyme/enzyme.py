# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from collections import OrderedDict

from gws_core import BadRequestException
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import (CharField, DeferredThroughModel, ForeignKeyField,
                    ManyToManyField)

from ..base.base_ft import BaseFT
from ..base.protected_base_model import ProtectedBaseModel
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
class Enzyme(BaseFT):
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
    bto = ManyToManyField(BTO, through_model=EnzymeBTODeffered)

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
        ec: str = self.ec_number
        ec_class = ".".join(ec.split(".")[0:-1]) + ".-"
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
        """ Get proteins """
        return Protein.get_or_none(Protein.uniprot_id == self.uniprot_id)

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
        """ Get pathways """
        return EnzymePathway.get_or_none(EnzymePathway.ec_number == self.ec_number)

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
    def related_deprecated_enzyme(self):
        """ Returns depreacated enzymes related to this enzyme """
        return DeprecatedEnzyme.get_or_none(DeprecatedEnzyme.new_ec_number == self.ec_number)

    @property
    def reactions(self):
        """
        Returns the list of reactions associated with the enzyme function
        :returns: List of reactions
        :rtype: Query rows
        """

        from ..reaction.reaction import Reaction, ReactionEnzyme
        query = Reaction.select() \
            .join(ReactionEnzyme) \
            .where(ReactionEnzyme.enzyme == self)
        return query

    # -- S --

    @classmethod
    def select_and_follow_if_deprecated(self, ec_number, tax_id=None, select_only_one=False, fields=None):
        """ Select deprecated enzymes """
        tax = None
        if tax_id:
            try:
                tax = Taxonomy.get(Taxonomy.tax_id == tax_id)
            except Exception as err:
                raise BadRequestException(f"Taxonomy ID {tax_id} not found") from err

        if fields:
            fields = [getattr(Enzyme, f) for f in fields]
            base_query = Enzyme.select(*fields)
        else:
            base_query = Enzyme.select()

        query = base_query.where(Enzyme.ec_number == ec_number)
        if tax:
            tax_field = getattr(Enzyme, "tax_"+tax.rank)
            query = query.where(tax_field == tax_id)
        if select_only_one:
            query = query.limit(1)

        if len(query) == 0:
            query = base_query.join(DeprecatedEnzyme, on=(Enzyme.ec_number == DeprecatedEnzyme.new_ec_number))\
                .where(DeprecatedEnzyme.ec_number == ec_number)
            if tax:
                tax_field = getattr(Enzyme, "tax_"+tax.rank)
                query = query.where(tax_field == tax_id)
            if select_only_one:
                query = query.limit(1)

        return query

    def save(self, *arg, **kwargs):
        if isinstance(self.data, OrderedDict):
            self.data = dict(self.data)
        return super().save(*arg, **kwargs)

    # -- T --

    @property
    def taxonomy(self):
        """ Returns taxonomy """
        return Taxonomy.get_or_none(Taxonomy.tax_id == self.tax_id)

    # -- U --


class EnzymeBTO(ProtectedBaseModel):
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

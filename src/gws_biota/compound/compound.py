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

from typing import Union

from gws_core import BadRequestException
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import (CharField, DoubleField, FloatField, ForeignKeyField,
                    IntegerField, ModelSelect, TextField)
from playhouse.mysql_ext import Match

from ..base.base import Base
from ..base.protected_base_model import ProtectedBaseModel
from ..db.db_manager import DbManager
from .compound_layout import CompoundLayout, CompoundLayoutDict


@typing_registrator(unique_name="Compound", object_type="MODEL", hide=True)
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
    mass = DoubleField(null=True, index=True)
    monoisotopic_mass = DoubleField(null=True, index=True)
    inchi = CharField(null=True, index=True)
    inchikey = CharField(null=True, index=True)
    smiles = CharField(null=True, index=True)
    chebi_star = CharField(null=True, index=True)
    ft_names = TextField(null=True)

    _ancestors = None
    _table_name = "biota_compound"

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

    @property
    def alt_chebi_ids(self) -> list:
        return sorted(self.data.get("alt_id"))

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
    def drop_table(cls, *arg, **kwargs):
        """
        Drops `Compound` table and related tables.

        Extra parameters are passed to :meth:`peewee.Model.drop_table`
        """
        CompoundAncestor.drop_table()
        super().drop_table(*arg, **kwargs)

    # -- G --

    @classmethod
    def search_by_chebi_ids(cls, chebi_ids: Union[list, str]):
        if isinstance(chebi_ids, list):
            chebi_ids = " ".join(chebi_ids)
        return cls.search(chebi_ids)

    # -- P --

    @property
    def layout(self) -> CompoundLayoutDict:
        alt_chebi_ids = self.alt_chebi_ids
        return CompoundLayout.get_layout_by_chebi_id(synonym_chebi_ids=[self.chebi_id, *alt_chebi_ids])

    @property
    def pathways(self):
        from .pathway import PathwayCompound

        try:
            pcomps = PathwayCompound.select().where(
                PathwayCompound.chebi_id == self.chebi_id
            )
            pathways = []
            for pc in pcomps:
                pw = pc.pathway
                if pw:
                    pathways.append(pc.pathway)

            return pathways
        except Exception as _:
            return None

    # -- R --

    @property
    def reactions(self):
        from .reaction import ReactionProduct, ReactionSubstrate

        rxns = []
        Q = ReactionSubstrate.select().where(ReactionSubstrate.compound == self)
        for r in Q:
            rxns.append(r.reaction)

        Q = ReactionProduct.select().where(ReactionProduct.compound == self)
        for r in Q:
            rxns.append(r.reaction)

        return rxns

    @classmethod
    def create_full_text_index(cls, *args) -> None:
        super().create_full_text_index(['ft_names'], 'I_F_BIOTA_CMP')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.ft_names), phrase, modifier=modifier))


# class CompoundAlternative(Base):
#     """
#     This class defines the many-to-many relationship between the compound and it alterntive ids

#     :type main_compound_chebi_id: CharField
#     :property main_compound_chebi_id: id of the concerned compound term
#     :type alt_compound_chebi_id: CharField
#     :property alt_compound_chebi_id: alternative of the concerned compound term
#     """

#     main_compound_chebi_id = CharField(null=True, index=True)
#     alt_compound_chebi_id = CharField(null=True, index=True)
#     _table_name = "biota_compound_alternatives"


class CompoundAncestor(ProtectedBaseModel):
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
        table_name = "biota_compound_ancestors"
        database = DbManager.db
        indexes = ((("compound", "ancestor"), True),)

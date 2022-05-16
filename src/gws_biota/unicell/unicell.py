# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com


import pickle

import numpy
from gws_core.model.typing_register_decorator import typing_registrator
from peewee import BigBitField, BlobField, CharField, ModelSelect, TextField
from playhouse.mysql_ext import Match
from scipy import sparse
from scipy.sparse.linalg import expm

from ..base.base import Base


@typing_registrator(unique_name="Unicell", object_type="MODEL", hide=True)
class Unicell(Base):
    """
    The unicell
    """

    ft_names = TextField(null=True, index=False)
    compound_id_list = BlobField()
    reaction_id_list = BlobField()
    stochiometric_matrix = BlobField()

    _compound_id_list = None
    _reaction_id_list = None
    _stochiometric_matrix = None

    _table_name = 'biota_unicell'

    @property
    def nb_compounds(self):
        """ Returns the number of compounds  """
        return len(self.get_compound_id_list())

    @property
    def nb_reactions(self):
        """ Returns the number of reactions  """
        return len(self.get_reaction_id_list())

    def get_compound_id_list(self):
        """ Get compound_id_list matrix """
        if self._compound_id_list is None:
            self._compound_id_list = pickle.loads(self.compound_id_list)
        return self._compound_id_list

    def get_reaction_id_list(self):
        """ Get reaction_id_list matrix """
        if self._reaction_id_list is None:
            self._reaction_id_list = pickle.loads(self.reaction_id_list)
        return self._reaction_id_list

    def get_stochiometric_matrix(self):
        """ Get stoichimetric matrix """
        if self._stochiometric_matrix is None:
            self._stochiometric_matrix = pickle.loads(self.stochiometric_matrix)
        return self._stochiometric_matrix

    def get_comp2comp_matrix(self):
        """ Get comp2comp incidence matrix """
        stochiometric_matrix = self.get_stochiometric_matrix()
        return stochiometric_matrix @ stochiometric_matrix.T

    def get_rxn2rxn_matrix(self):
        """ Get rxn2rxn incidence matrix """
        stochiometric_matrix = self.get_stochiometric_matrix()
        return stochiometric_matrix.T @ stochiometric_matrix

    def get_compound_id_at(self, i) -> int:
        """ Get index of a compound using its chebi_id """
        comp_list = self.get_compound_id_list()
        return comp_list[i]

    def get_index_of_compound_id(self, chebi_id) -> str:
        """ Get chebi_id at a given index """
        comp_list = self.get_compound_id_list()
        return comp_list.index(chebi_id)

    def get_reaction_id_at(self, i) -> str:
        """ Get rhea_id at a given index """
        rxn_list = self.get_reaction_id_list()
        return rxn_list[i]

    def get_index_of_reaction_id(self, rhea_id) -> int:
        """ Get index of a reaction using its rhea_id """
        rxn_list = self.get_reaction_id_list()
        return rxn_list.index(rhea_id)

    @classmethod
    def after_table_creation(cls) -> None:
        cls.create_full_text_index(['ft_names'], 'I_F_BIOTA_UNICELL')

    @classmethod
    def search(cls, phrase: str, modifier: str = None) -> ModelSelect:
        return cls.select().where(Match((cls.ft_names), phrase, modifier=modifier))

    def write(self, **kwargs):
        """ write an entry """
        uc = Unicell(
            compound_id_list=pickle.dumps(kwargs["compound_id_list"]),
            comp_index_to_chebi=pickle.dumps(kwargs["comp_index_to_chebi"]),
            reaction_id_list=pickle.dumps(kwargs["reaction_id_list"]),
            rxn_index_to_rhea=pickle.dumps(kwargs["rxn_index_to_rhea"]),
            stochiometric_matrix=pickle.dumps(kwargs["stochiometric_matrix"]),
        )
        uc.save()

    def create_compound_vertor(self, chebi_id):
        m = self.nb_compounds()
        vec = numpy.zeros((m, 1))
        idx = self.get_index_of_compound_id(chebi_id)
        vec[idx] = 1
        return sparse.csr_array(vec)

    def are_connected(self, chebi_id1, chebi_id2) -> bool:
        x = self.create_compound_vertor(chebi_id1)
        A = self.get_comp2comp_matrix()
        y = x @ linalg.expm(A)

        idx = self.get_index_of_compound_id(chebi_id2)
        return bool(y[idx, 1])

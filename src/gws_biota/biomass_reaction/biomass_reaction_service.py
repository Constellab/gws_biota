


import os
from gws_core import transaction
from .biomass_reaction import BiomassReaction
from .._helper.biomass_reaction import BiomassReaction as BiomassReactionHelper
from ..base.base_service import BaseService

class BiomassReactionService(BaseService):
    
    @classmethod
    @transaction()
    def create_biomass_reaction_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `network` database

        :param biodata_dir: path to the folder that contain the :file:`sbo.obo` file
        :type biodata_dir: str
        :param files_test: dictionnary that contains all data files names
        :type files_test: dict
        :returns: None
        :rtype: None
        """

        file = os.path.join(biodata_dir, kwargs["network_file"])
        data = BiomassReactionHelper.extract_biomass_reactions_from_file(file)

        for d in data:
            brxn = BiomassReaction()
            brxn.biomass_rxn_id = d["id"]
            brxn.set_name = d["name"]
            brxn.data = d
            brxn.ft_names = ",".join(["biomass", d["name"], *d["id"].split("_")])
            brxn.save()
# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from peewee import CharField
from .._helper.expasy import Expasy
from ..base.base import Base

class EnzymeClass(Base):
    
    ec_number = CharField(null=True, index=True, unique=True)
    _table_name = 'biota_enzyme_class'
    
    # -- C --

    @classmethod
    def create_enzyme_class_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `enzyme_class` database

        :param biodata_dir: path of the :file:`enzclass.txt`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """

        list_of_enzclasses = Expasy.parse_all_enzclasses_to_dict(biodata_dir, kwargs['expasy_enzclass_file'])
        enz_classes = []
        for enzc in list_of_enzclasses:
            ec = EnzymeClass(
                ec_number = enzc["ec_number"],
                data = enzc["data"]
            )
            ec.set_name( enzc["data"]["name"] )
            enz_classes.append(ec)
        EnzymeClass.save_all(enz_classes)

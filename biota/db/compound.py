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

from peewee import CharField, FloatField, IntegerField
from biota.db.base import Base

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
    charge = FloatField(null=True, index=True)
    mass = FloatField(null=True, index=True)
    monoisotopic_mass = FloatField(null=True, index=True)
    inchi = CharField(null=True, index=True)
    inchikey = CharField(null=True, index=True)
    smiles = CharField(null=True, index=True)
    chebi_star = CharField(null=True, index=True)

    _fts_fields = { **Base._fts_fields, 'synonyms': 2.0, 'definition': 1.0}
    _table_name = 'compound'

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

        from biota._helper.chebi import Chebi as ChebiHelper

        data_dir, corrected_file_name = ChebiHelper.correction_of_chebi_file(biodata_dir, kwargs['chebi_file'])

        onto = ChebiHelper.create_ontology_from_file(data_dir, corrected_file_name)
        list_chebi = ChebiHelper.parse_onto_from_ontology(onto)
        chebis = [cls(data = dict_) for dict_ in list_chebi]
        job = kwargs.get('job',None)
        
        for chebi in chebis:
            chebi.set_name(chebi.data["title"])
            chebi.chebi_id = chebi.data["id"]
            
            chebi.inchi = chebi.data["inchi"]
            chebi.inchikey = chebi.data["inchikey"]
            chebi.smiles = chebi.data["smiles"]
            chebi.mass = chebi.data["mass"]
            chebi.monoisotopic_mass = chebi.data["monoisotopic_mass"]
            chebi.charge = chebi.data["charge"]
            chebi.chebi_star = chebi.data["subsets"]
            
            if "kegg" in chebi.data["xref"]:
                chebi.kegg_id = chebi.data["xref"]["kegg"]
                del chebi.data["xref"]["kegg"]

            if "metacyc" in chebi.data["xref"]:
                chebi.metacyc_id = chebi.data["xref"]["metacyc"]
                del chebi.data["xref"]["metacyc"]

            del chebi.data["id"]
            del chebi.data["inchi"]
            del chebi.data["inchikey"]
            del chebi.data["smiles"]
            del chebi.data["mass"]
            del chebi.data["monoisotopic_mass"]
            del chebi.data["charge"]
            del chebi.data["subsets"]

            if not job is None:
                chebi._set_job(job)

        cls.save_all(chebis)
        return(list_chebi)

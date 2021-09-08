# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os

from gws_core import transaction
from .._helper.brenda import Brenda
from .._helper.bkms import BKMS
from ..taxonomy.taxonomy import Taxonomy
from ..bto.bto import BTO
from .enzyme import Enzyme
from .enzyme_class import EnzymeClass
from .deprecated_enzyme import DeprecatedEnzyme
from .enzyme_pathway import EnzymePathway
from .enzyme_ortholog import EnzymeOrtholog

class EnzymeService:
    
    @classmethod
    @transaction()
    def create_enzyme_db(cls, biodata_dir = None, **kwargs):
        """
        Creates and fills the `enzyme` database

        :param biodata_dir: path of the :file:`go.obo`
        :type biodata_dir: str
        :param files: dictionnary that contains all data files names
        :type files: dict
        :returns: None
        :rtype: None
        """
        
        # add enzyme classes
        EnzymeClass.create_enzyme_class_db(biodata_dir, **kwargs)
        # add enzymes
        brenda = Brenda(os.path.join(biodata_dir, kwargs['brenda_file']))
        list_of_enzymes, list_deprecated_ec = brenda.parse_all_enzyme_to_dict()
        # saved all deprecated enzymes
        deprecated_enzymes = []
        for dep_ec in list_deprecated_ec:
            if dep_ec["new_ec"]:
                for ne in dep_ec["new_ec"]:
                    t_enz = DeprecatedEnzyme(
                        ec_number=dep_ec["old_ec"], 
                        new_ec_number=ne,
                        data = dep_ec["data"]
                    )
                    deprecated_enzymes.append(t_enz)
            else:
                t_enz = DeprecatedEnzyme(
                    ec_number=dep_ec["old_ec"], 
                    data = dep_ec["data"]
                )
                deprecated_enzymes.append(t_enz)
            
        if deprecated_enzymes:
            DeprecatedEnzyme.save_all(deprecated_enzymes)
 
        # save EnzymePathway
        pathways = {}
        for d in list_of_enzymes:
            ec = d['ec']
            if not ec in pathways:
                pathways[ec] = EnzymePathway(ec_number = ec)
        EnzymePathway.save_all(pathways.values())

        # save EnzymeOrtholog
        enzos = {}
        for d in list_of_enzymes:
            ec = d['ec']
            if not ec in enzos:
                enzos[ec] = EnzymeOrtholog(
                    ec_number = ec,
                    data = {
                        'RN': d['RN'],
                        'SN': d.get('SN', []),
                        'SY': d.get('SY', [])
                    }
                )
                enzos[ec].set_name(d['RN'][0])
                enzos[ec].pathway = pathways[ec]
        EnzymeOrtholog.save_all(enzos.values())
        
        # save Enzymes
        enzymes = []
        for d in list_of_enzymes:
            ec = d['ec']
            enz = Enzyme(
                ec_number = ec,
                uniprot_id = d["uniprot"],
                data = d
            )
            enz.set_name(d['RN'][0])
            enzymes.append(enz)
        Enzyme.save_all(enzymes)
        
        # save taxonomy and t
        cls.__update_tax_tissue(enzymes)  
        
        # save bkms data
        if 'bkms_file' in kwargs:
            list_of_bkms = BKMS.parse_csv_from_file(biodata_dir, kwargs['bkms_file'])
            cls.__update_pathway_from_bkms(list_of_bkms)
        
     
    # -- U --

    @classmethod
    def __update_tax_tissue(cls, enzymes):
        for enz in enzymes:
            cls.__update_taxonomy(enz)
            cls.__update_tissues(enz)
        Enzyme.save_all(enzymes)

    @classmethod
    def __update_taxonomy(self, enzyme):
        """
        See if there is any information about the enzyme taxonomy and if so, connects
        the enzyme and its taxonomy by adding the related tax_id from the taxonomy 
        table to the taxonomy property of the enzyme
        """
  
        if 'taxonomy' in enzyme.data:
            try:
                enzyme.tax_id = str(enzyme.data['taxonomy'])
                tax = Taxonomy.get(Taxonomy.tax_id == enzyme.tax_id)
                setattr(enzyme, "tax_"+tax.rank, tax.tax_id)
                for t in tax.ancestors:  
                    if t.rank in Taxonomy._tax_tree:
                        setattr(enzyme, "tax_"+t.rank, t.tax_id)        
                del enzyme.data['taxonomy']
            except:
                pass
    
    @classmethod
    def __update_tissues(self, enzyme):
        """
        See if there is any information about the enzyme tissue locations and if so, 
        connects the enzyme and tissues by adding an enzyme-tissues relation 
        in the enzyme_btos table
        """

        n = len(enzyme.params('ST'))
        bto_ids = []
        for i in range(0,n):
            bto_ids.append( enzyme.params('ST')[i].get("bto") )
        Q = BTO.select().where(BTO.bto_id << bto_ids)
        for bto in Q: 
            enzyme.bto.add(bto)

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the enzyme tissue locations and if so, 
        connects the enzyme and tissues by adding an enzyme-tissues relation 
        in the enzyme_btostable
        """

        pathways = {}
        bulk_size = 750
        dbs = ['brenda', 'kegg', 'metacyc']
        for bkms in list_of_bkms:
            ec_number = bkms["ec_number"]
            Q = EnzymePathway.select().where(EnzymePathway.ec_number == ec_number)
            for pathway in Q:
                for k in dbs:

                    if bkms.get(k+'_pathway_name'):
                        #pwy_id = bkms.get(k+'_pathway_id', "ID")
                        #pwy_name = bkms[k+'_pathway_name']
                        #pathway.data[k+'_pathway'] = { pwy_id : pwy_name }
                        pwy_id = bkms.get(k+'_pathway_id', "")
                        pwy_name = bkms[k+'_pathway_name']
                        pathway.data[k] = { 
                            "id": pwy_id,
                            "name": pwy_name 
                        }
                pathways[pathway.ec_number] = pathway
                if len(pathways.keys()) >= bulk_size:
                    EnzymePathway.save_all(pathways.values())
                    pathways = {}
        if len(pathways) > 0:
            EnzymePathway.save_all(pathways.values())

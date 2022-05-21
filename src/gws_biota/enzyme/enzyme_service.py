# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os

from gws_core import transaction, Logger

from .._helper.bkms import BKMS
from .._helper.brenda import Brenda
from ..bto.bto import BTO
from ..taxonomy.taxonomy import Taxonomy
from .deprecated_enzyme import DeprecatedEnzyme
from .enzyme import Enzyme, EnzymeBTO
from .enzyme_class import EnzymeClass
from .enzyme_ortholog import EnzymeOrtholog
from .enzyme_pathway import EnzymePathway
from ..base.base_service import BaseService

class EnzymeService(BaseService):
    @classmethod
    @transaction()
    def create_enzyme_db(cls, biodata_dir=None, **kwargs):
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
        Logger.info(f"Loading BRENDA file ...")
        EnzymeClass.create_enzyme_class_db(biodata_dir, **kwargs)
        brenda = Brenda(os.path.join(biodata_dir, kwargs["brenda_file"]))
        list_of_enzymes, list_deprecated_ec = brenda.parse_all_enzyme_to_dict()
        
        # save EnzymePathway
        Logger.info(f"Saving enzyme pathways ...")
        pathways = {}
        for d in list_of_enzymes:
            ec = d["ec"]
            if not ec in pathways:
                pathways[ec] = EnzymePathway(ec_number=ec)
        EnzymePathway.save_all(pathways.values())

        # save EnzymeOrtholog
        Logger.info(f"Saving enzyme orthologs ...")
        enzos = {}
        for d in list_of_enzymes:
            ec = d["ec"]
            if not ec in enzos:
                rn = d["RN"]
                sn = d.get("SN", [])
                sy = [k.get("data", "") for k in d.get("SY", [])]
                ft_names = [ec.replace(".",""), *rn, *sn, *sy]
                enzos[ec] = EnzymeOrtholog(
                    ec_number=ec,
                    data={"RN": rn, "SN": sn, "SY": sy},
                    ft_names=cls.format_ft_names(ft_names),
                )
                enzos[ec].set_name(d["RN"][0])
                enzos[ec].pathway = pathways[ec]
        EnzymeOrtholog.save_all(enzos.values())

        # save Enzymes
        Logger.info(f"Saving enzymes ...")
        enzymes = []
        for d in list_of_enzymes:
            ec = d["ec"]
            rn = d["RN"]
            sn = d.get("SN", [])
            sy = [k.get("data", "") for k in d.get("SY", [])]
            organism = d.get("organism")
            enz = Enzyme(
                ec_number=ec,
                uniprot_id=d["uniprot"],
                data=d,
                ft_names=";".join([ec.replace(".",""), *rn, *sn, *sy, organism]),
            )
            enz.set_name(d["RN"][0])
            enzymes.append(enz)
        Enzyme.save_all(enzymes)
    
        
        def _get_new_enzyme_info(old_ec_numner):
            info = []
            for dep_ec in list_deprecated_ec:
                if dep_ec["old_ec"] == old_ec_numner:
                    if dep_ec["new_ec"]:
                        for new_ec in dep_ec["new_ec"]:
                            count = EnzymeOrtholog.select().where(EnzymeOrtholog.ec_number == new_ec).count()
                            if count:
                                info.append({
                                    "new_ec": new_ec,
                                    "data": dep_ec["data"]
                                })
                            else:
                                current_info = _get_new_enzyme_info(new_ec)
                                info.extends(current_info)
                        break
                break
            return info

        # saved all deprecated enzymes
        Logger.info(f"Saving deprecated enzymes ...")
        deprecated_enzymes = []
        for dep_ec in list_deprecated_ec:
            old_ec = dep_ec["old_ec"]
            all_info = _get_new_enzyme_info(old_ec)
            for info in all_info:
                t_enz = DeprecatedEnzyme(
                    ec_number=old_ec,
                    new_ec_number=info["new_ec"],
                    data=info["data"],
                )
                deprecated_enzymes.append(t_enz)

        if deprecated_enzymes:
            DeprecatedEnzyme.save_all(deprecated_enzymes)
            
        # save taxonomy
        Logger.info(f"Updating enzyme taxonomy ...")
        cls.__update_taxonomy(enzymes)

        Logger.info(f"Updating enzyme bto ...")
        cls.__update_bto(enzymes)

        # save bkms data
        Logger.info(f"Updating enzyme BKMS data ...")
        if "bkms_file" in kwargs:
            list_of_bkms = BKMS.parse_csv_from_file(biodata_dir, kwargs["bkms_file"])
            cls.__update_pathway_from_bkms(list_of_bkms)
        
    # -- U --

    @classmethod
    def __update_taxonomy(cls, enzymes):
        for enz in enzymes:
            cls.__set_taxonomy_data(enz)
        fields = [ "tax_"+t for t in Taxonomy._tax_tree ]
        Enzyme.update_all(enzymes, fields=[ "tax_id", *fields])

    @classmethod
    def __update_bto(cls, enzymes):
        vals = []
        for enz in enzymes:
            vals.extend( cls.__create_bto_values(enz) )
        EnzymeBTO.insert_all(vals)
        
    @classmethod
    def __set_taxonomy_data(self, enzyme):
        """
        See if there is any information about the enzyme taxonomy and if so, connects
        the enzyme and its taxonomy by adding the related tax_id from the taxonomy
        table to the taxonomy property of the enzyme
        """

        if "taxonomy" in enzyme.data:
            try:
                enzyme.tax_id = str(enzyme.data["taxonomy"])
                tax = Taxonomy.get(Taxonomy.tax_id == enzyme.tax_id)
                setattr(enzyme, "tax_" + tax.rank, tax.tax_id)
                for t in tax.ancestors:
                    if t.rank in Taxonomy._tax_tree:
                        setattr(enzyme, "tax_" + t.rank, t.tax_id)
                del enzyme.data["taxonomy"]
            except:
                pass

    @classmethod
    def __create_bto_values(self, enzyme):
        """
        See if there is any information about the enzyme tissue locations and if so,
        connects the enzyme and tissues by adding an enzyme-tissues relation
        in the enzyme_btos table
        """

        n = len(enzyme.params("ST"))
        bto_ids = []
        for i in range(0, n):
            bto_ids.append(enzyme.params("ST")[i].get("bto"))
        Q = BTO.select().where(BTO.bto_id << bto_ids)
        
        vals = []
        for bto in Q:
            vals.append( {'bto': bto.id, 'enzyme': enzyme.id} )
        return vals

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the enzyme tissue locations and if so,
        connects the enzyme and tissues by adding an enzyme-tissues relation
        in the enzyme_btostable
        """

        pathways = {}
        dbs = ["brenda", "kegg", "metacyc"]
        for bkms in list_of_bkms:
            ec_number = bkms["ec_number"]
            Q = EnzymePathway.select().where(EnzymePathway.ec_number == ec_number)
            for pathway in Q:
                for k in dbs:
                    if bkms.get(k + "_pathway_name"):
                        pwy_id = bkms.get(k + "_pathway_id", "")
                        pwy_name = bkms[k + "_pathway_name"]
                        pathway.data[k] = {"id": pwy_id, "name": pwy_name}
                
                pathways[pathway.ec_number] = pathway

        EnzymePathway.update_all(pathways.values(), fields=['data'])

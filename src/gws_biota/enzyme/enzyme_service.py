# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import Logger, transaction, Settings
from peewee import chunked

from .._helper.bkms import BKMS
from .._helper.brenda import Brenda
from ..base.base_service import BaseService
from ..bto.bto import BTO
from ..taxonomy.taxonomy import Taxonomy
from .deprecated_enzyme import DeprecatedEnzyme
from .enzyme import Enzyme, EnzymeBTO
from .enzyme_class import EnzymeClass
from .enzyme_ortholog import EnzymeOrtholog
from .enzyme_pathway import EnzymePathway


class EnzymeService(BaseService):
    @classmethod
    @transaction()
    def create_enzyme_db(cls, brenda_file, bkms_file, expasy_file, taxonomy_file, bto_file, compound_file):
        """
        Creates and fills the `enzyme` database
        :param: enzymes files
        :type files: file
        :returns: None
        :rtype: None
        """

        base_biodata_dir = Settings.get_instance().get_variable("gws_biota:biodata_dir")

        # add enzyme classes
        Logger.info("Loading BRENDA file ...")
        EnzymeClass.create_enzyme_class_db(base_biodata_dir, expasy_file)
        brenda = Brenda(
            brenda_file=brenda_file,
            taxonomy_dir=taxonomy_file,
            bto_file=bto_file,
            chebi_file=compound_file,
        )

        list_of_enzymes, list_deprecated_ec = brenda.parse_all_enzyme_to_dict()

        # save EnzymePathway
        Logger.info("Saving enzyme pathways ...")
        pathways = {}
        for d in list_of_enzymes:
            ec = d["ec"]
            if not ec in pathways:
                pathways[ec] = EnzymePathway(ec_number=ec)
        EnzymePathway.create_all(pathways.values())

        # save EnzymeOrtholog
        Logger.info("Saving enzyme orthologs ...")
        enzos = {}
        for d in list_of_enzymes:
            ec = d["ec"]
            if not ec in enzos:
                rn = d["RN"]
                sn = d.get("SN", [])
                sy = [k.get("data", "") for k in d.get("SY", [])]
                ft_names = ["EC"+ec.replace(".", ""), *rn, *sn, *sy]
                enzos[ec] = EnzymeOrtholog(
                    ec_number=ec,
                    data={"RN": rn, "SN": sn, "SY": sy},
                    ft_names=cls.format_ft_names(ft_names),
                )
                enzos[ec].set_name(d["RN"][0])
                enzos[ec].pathway = pathways[ec]
        EnzymeOrtholog.create_all(enzos.values())

        # save Enzymes
        Logger.info("Saving enzymes ...")
        enzymes = []
        enz_count = len(list_of_enzymes)
        i = 0
        for chunk in chunked(list_of_enzymes, cls.BATCH_SIZE):
            i += 1
            enzyme_chunk = []
            Logger.info(f"... saving enzyme chunk {i}/{int(enz_count/cls.BATCH_SIZE)+1}")
            for d in chunk:
                ec = d["ec"]
                rn = d["RN"]
                sn = d.get("SN", [])
                sy = [k.get("data", "") for k in d.get("SY", [])]
                organism = d.get("organism")
                enz = Enzyme(
                    ec_number=ec,
                    uniprot_id=d["uniprot"],
                    data=d,
                    ft_names=";".join([
                        "EC"+ec.replace(".", ""),
                        *rn, *sn, *sy, organism
                    ]),
                )
                enz.set_name(d["RN"][0])
                enzyme_chunk.append(enz)
            Enzyme.create_all(enzyme_chunk)
            enzymes.extend(enzyme_chunk)

        # flatten the list_deprecated_ec
        all_old_ecs = [elt["old_ec"] for elt in list_deprecated_ec]
        # list_deprecated_ec = {elt["old_ec"]: elt for elt in list_deprecated_ec if len(elt["new_ec"]) > 0}
        list_deprecated_ec = {elt["old_ec"]: elt for elt in list_deprecated_ec}
        is_nested = True
        while is_nested:
            is_nested = False
            for dep_ec in list_deprecated_ec.values():
                new_list = []
                for new_ec in dep_ec["new_ec"]:
                    if new_ec in all_old_ecs:
                        # follow nested ...
                        is_nested = True
                        if new_ec == dep_ec["old_ec"]:
                            # pathologic cyclic dependency
                            dep_ec["new_ec"].remove(new_ec)
                        if new_ec in list_deprecated_ec:
                            # take the nested relation
                            next_dep_ec = list_deprecated_ec[new_ec]
                            # dep_ec["new_ec"] = next_dep_ec["new_ec"]  # follow the next
                            new_list.extend(next_dep_ec["new_ec"])  # follow the next
                            new_list = list(set(new_list))
                            for key, val in next_dep_ec["data"].items():
                                # concatenate the next data with the current one
                                dep_ec["data"][key] += ";" + val
                        else:
                            # the next relation does not exist ... this deprecated enzyme was probably deleted
                            dep_ec["data"]["reason"] += f"; {new_ec} probably deleted"
                    else:
                        new_list.append(new_ec)
                        new_list = list(set(new_list))
                dep_ec["new_ec"] = new_list

        # list_deprecated_ec = {elt["old_ec"]: elt for elt in list_deprecated_ec.values() if len(elt["new_ec"]) > 0}

        # saved all deprecated enzymes
        Logger.info("Saving deprecated enzymes ...")
        deprecated_enzymes = []
        for old_ec, elt in list_deprecated_ec.items():
            if len(elt["new_ec"]) == 0:
                elt["new_ec"] = [None]

            for new_ec in elt["new_ec"]:
                t_enz = DeprecatedEnzyme(
                    ec_number=old_ec,
                    new_ec_number=new_ec,
                    data=elt["data"],
                )
                deprecated_enzymes.append(t_enz)

        if deprecated_enzymes:
            DeprecatedEnzyme.create_all(deprecated_enzymes)

        # save taxonomy
        Logger.info("Updating enzyme taxonomy ...")
        cls.__update_taxonomy(enzymes)

        Logger.info("Updating enzyme bto ...")
        cls.__update_bto(enzymes)

        # save bkms data
        Logger.info("Updating enzyme BKMS data ...")
        list_of_bkms = BKMS.parse_csv_from_file(base_biodata_dir, bkms_file)
        cls.__update_pathway_from_bkms(list_of_bkms)

    # -- U --

    @classmethod
    def __update_taxonomy(cls, enzymes):
        for enz in enzymes:
            cls.__set_taxonomy_data(enz)
        fields = ["tax_"+t for t in Taxonomy.get_tax_tree()]
        Enzyme.update_all(enzymes, fields=["tax_id", *fields])

    @classmethod
    def __update_bto(cls, enzymes):
        vals = []
        for enz in enzymes:
            vals.extend(cls.__create_bto_values(enz))
        EnzymeBTO.insert_all(vals)

    @classmethod
    def __set_taxonomy_data(cls, enzyme):
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
                    if t.rank in Taxonomy.get_tax_tree():
                        setattr(enzyme, "tax_" + t.rank, t.tax_id)
                del enzyme.data["taxonomy"]
            except Exception as _:
                pass

    @classmethod
    def __create_bto_values(cls, enzyme):
        """
        See if there is any information about the enzyme tissue locations and if so,
        connects the enzyme and tissues by adding an enzyme-tissues relation
        in the enzyme_btos table
        """

        n = len(enzyme.get_params("ST"))
        bto_ids = []
        for i in range(0, n):
            bto_ids.append(enzyme.get_params("ST")[i].get("bto"))
        Q = BTO.select().where(BTO.bto_id << bto_ids)

        vals = []
        for bto in Q:
            vals.append({'bto': bto.id, 'enzyme': enzyme.id})
        return vals

    @classmethod
    def __update_pathway_from_bkms(cls, list_of_bkms):
        """
        See if there is any information about the biochemical reaction and if so,
        connects the enzyme and biochemical reaction by adding an enzyme-bkms relation
        in the biota_enzyme_pathway
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

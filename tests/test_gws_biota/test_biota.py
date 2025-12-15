import json
import os

from gws_biota import BiomassReaction, Compound
from gws_biota.biomass_reaction.biomass_reaction_service import BiomassReactionService
from gws_core import BaseTestCase, Settings

settings = Settings.get_instance()
testdata_path = settings.get_variable("gws_biota", "testdata_dir")


class TestBiotaReaction(BaseTestCase):
    def test_db_object(self):
        self.print("BiomassReaction")
        params = dict(
            biodata_dir=testdata_path,
            network_file="ecoli_core.json",
        )

        # create compound DB first
        file = os.path.join(testdata_path, "ecoli_core.json")
        with open(file, encoding="utf-8") as fp:
            data = json.load(fp)
            ckey = "compounds" if "compounds" in data else "metabolites"
            compounds = data[ckey]
            reactions = data["reactions"]
            for comp_data in data[ckey]:
                chebi_ids = comp_data["annotation"].get("chebi")
                if chebi_ids:
                    comp = Compound(
                        chebi_id=chebi_ids[0],
                    )
                comp.set_name(comp_data["name"])
                comp.ft_names = ",".join(
                    [comp_data["name"], *[_id.replace("CHEBI:", "") for _id in chebi_ids]]
                )
                comp.save()

        Q = Compound.select()
        print(f"{len(Q)} compounds created")
        self.assertEqual(len(Q), 72)

        data = BiomassReactionService.create_biomass_reaction_db(**params)

        Q = BiomassReaction.select()
        print(len(Q))
        self.assertEqual(len(Q), 1)
        print(Q[0].data)

        self.assertEqual(Q[0].data["name"], "Biomass Objective Function with GAM")
        self.assertEqual(
            Q[0].data["definition"],
            "1.496 3_Phospho_D_glycerate + 3.7478 Acetyl_CoA + 59.81 ATP_C10H12N5O13P3 + 0.361 D_Erythrose_4_phosphate + 0.0709 D_Fructose_6_phosphate + 0.129 Glyceraldehyde_3_phosphate + 0.205 D_Glucose_6_phosphate + 0.2557 L_Glutamine + 4.9414 L_Glutamate + 59.81 H2O_H2O + 3.547 Nicotinamide_adenine_dinucleotide + 13.0279 Nicotinamide_adenine_dinucleotide_phosphate_reduced + 1.7867 Oxaloacetate + 0.5191 Phosphoenolpyruvate + 2.8328 Pyruvate + 0.8977 Alpha_D_Ribose_5_phosphate = 59.81 ADP_C10H12N5O10P2 + 4.1182 2_Oxoglutarate + 3.7478 Coenzyme_A + 59.81 H + 3.547 Nicotinamide_adenine_dinucleotide_reduced + 13.0279 Nicotinamide_adenine_dinucleotide_phosphate + 59.81 Phosphate",
        )

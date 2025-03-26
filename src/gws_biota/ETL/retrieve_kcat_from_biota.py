# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (ConfigParams, OutputSpec, OutputSpecs, Task, TaskInputs, ConfigSpecs,
                      task_decorator, Table, StrParam, Table,
                      TypingStyle)

from gws_biota import Enzyme
import numpy as np
import pandas as pd


@task_decorator("RetrieveKcatFromBiota", style=TypingStyle.material_icon(
    material_icon_name="database", background_color="#2b6d57"),
    human_name="Retrieve Kcat from BIOTA",
    short_description="Add kcat to ec number using BIOTA for a selected species")
class RetrieveKcatFromBiota(Task):
    output_specs = OutputSpecs({'results': OutputSpec(Table, human_name="Ec number to kcat",
                                                      short_description="Correspondence table between kcat and ec number")})

    config_specs = ConfigSpecs(
        {"organism_name": StrParam(default_value="Saccharomyces cerevisiae")})

    # --------------------- RUN ---------------------
    def run(self, params: ConfigParams, inputs: TaskInputs) -> Table:
        enzymes = Enzyme.select()
        enzymes_dict: dict = {}

        for enzyme in enzymes:
            if enzyme.organism == params["organism_name"]:
                ec_number = enzyme.ec_number
                n = len(enzyme.get_params('TN'))  # TN = turn over = kcat

                for i in range(0, n):
                    # Retrieve only value and substrate name of TN and not all data about it
                    tn_param = enzyme.get_params('TN')[i].value
                    if "{more}" in tn_param or len(tn_param) == 0:  # not a value
                        continue

                    if ec_number not in enzymes_dict:
                        enzymes_dict[ec_number] = []

                    # split value and substrate name
                    tn_param_values = tn_param.split(" ")
                    tn_value = tn_param_values[0]
                    # does not take into account values with a dash, so cannot be used to make a median => e.g. on brenda: for saccharomyces cerevisiae EC 4.1.1.23, TN 14-20 for substrate orotidine 5'-phosphate
                    if "-" in tn_value:
                        continue

                    tn_substrat = tn_param_values[1]
                    enzymes_dict[ec_number].append(
                        (float(tn_value), tn_substrat))

        enzymes_dict_normalize = {}
        for ec, tn_values in enzymes_dict.items():
            list_tn = []

            for tn in tn_values:
                list_tn.append(tn[0])  # take tn_value and not tn_substrat

            # Make the median of TN and ignore NaN
            tn_median = np.nanmedian(list_tn)

            enzymes_dict_normalize[ec] = tn_median

        df = pd.DataFrame(list(enzymes_dict_normalize.items()),
                          columns=['Ec number', 'median Kcat'])

        return {"results": Table(df)}

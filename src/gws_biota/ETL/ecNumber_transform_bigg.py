# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (ConfigParams, OutputSpec, OutputSpecs, Task, TaskInputs,
                      task_decorator, InputSpec, InputSpecs, Table, StrParam, File)

import json
import pandas as pd


@task_decorator("EcNumberTransformBiGG", human_name="Translate EC number to Bigg ID",
                short_description="Transform table corresponding to EC Number to BiGG id")
class EcNumberTransformBiGG(Task):
    input_specs = InputSpecs({'ec_number_table': InputSpec(Table, human_name="Table containing ec number"),
                              "BiGG_models": InputSpec(File, human_name="BiGG Models file about organism of internet")})
    output_specs = OutputSpecs({'table_results': OutputSpec(Table, human_name="Results",
                               short_description="Table containing the correspondance between bigg id, ec_number and kcat")})

    config_specs = {"organism_name": StrParam(default_value="Saccharomyces cerevisiae"),
                    "model_BiGG_id": StrParam(default_value="iMM904")}
    # --------------------- RUN ---------------------

    def run(self, params: ConfigParams, inputs: TaskInputs) -> Table:
        ec_numbers_table: Table = inputs['ec_number_table']
        BiGG_model: File = inputs["BiGG_models"]

        final_table = {}
        results = []

        with open(BiGG_model.path, "r") as bigg:
            data = json.load(bigg)

        # Retrieve bigg ID and ec-code from BiGG model file
        for reaction in data['reactions']:
            bigg_id = reaction.get('id', 'id not found')
            ec_code = reaction.get('annotation', {}).get('ec-code', 'EC not found')

            # If there is no data (ie. no bigg id and no ec-code), don't append to the results list; else write it
            if bigg_id != "id not found" and ec_code != "EC not found":
                results.append({'bigg_id': bigg_id, 'ec_code': ec_code})

        for ec_number, kcat in zip(ec_numbers_table.get_column_data(column_name="Ec number"),
                                   ec_numbers_table.get_column_data(column_name="median Kcat")):
            for info_bigg in results:
                # If there is a correspondance between ec number from ec_numbers_table and ec-code from bigg models file, add data to final_table
                if ec_number in info_bigg["ec_code"]:
                    final_table[ec_number] = {"bigg_id": info_bigg["bigg_id"], "median Kcat": kcat}

        # Flatten final_table to obtain a data_list that will be transformed into a dataframe
        data_list = [{'Ec number': ec, 'BiGG ID': details['bigg_id'], 'median Kcat': details['median Kcat']}
                     for ec, details in final_table.items()]

        df = pd.DataFrame(data_list)

        return {"table_results": Table(df)}

# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (ConfigParams, OutputSpec, OutputSpecs, Task, TaskInputs,
                      task_decorator, File, InputSpec, InputSpecs, StrParam, Table)


import pandas as pd


@task_decorator("CreateContextFile", human_name="Create file with reactions and kcat",
                short_description="Creation of the enzymatic context file used to reconstruct a metabolic network")
class CreateContextFile(Task):
    input_specs = InputSpecs({'reaction_table': InputSpec(
        Table, human_name="Table containing ec number, bigg id and kcat")})

    output_specs = OutputSpecs({'context_results': OutputSpec(File, human_name="Context results",
                                                              short_description="Context file used for twins")})

    config_specs = {"organism_name": StrParam(default_value="Saccharomyces cerevisiae")}

    # --------------------- RUN ---------------------
    def run(self, params: ConfigParams, inputs: TaskInputs) -> File:
        reaction_table: Table = pd.DataFrame(inputs['reaction_table'].get_data())

        organism_name: str = params["organism_name"]

        with open(f"reaction_kcat_{organism_name}.txt", "w") as context:
            # example of line => NTD8,1.100,0.100,2.100,1
            context.write("reaction_id,target,lower_bound,upper_bound,confidence_score\n")
            for ec, bigg, kcat in zip(
                    reaction_table["Ec number"],
                    reaction_table["BiGG ID"],
                    reaction_table["median Kcat"]):
                context.write(
                    f"{bigg},{kcat:.3f},{kcat - 1:.3f},{kcat + 1:.3f},1\n")

        return {"context_results": File(f"reaction_kcat_{organism_name}.txt")}

from typing import cast

from gws_core import (
    AppConfig,
    AppType,
    BoolParam,
    ConfigParams,
    ConfigSpecs,
    File,
    InputSpec,
    InputSpecs,
    OutputSpec,
    OutputSpecs,
    ReflexResource,
    StrParam,
    Task,
    TaskInputs,
    TaskOutputs,
    app_decorator,
    task_decorator,
)


@app_decorator("BiotaAppAppConfig", app_type=AppType.REFLEX, human_name="Generate BiotaApp app")
class BiotaAppAppConfig(AppConfig):
    # retrieve the path of the app folder, relative to this file
    # the app code folder starts with a underscore to avoid being loaded when the brick is loaded
    def get_app_folder_path(self):
        return self.get_app_folder_from_relative_path(__file__, "_biota_app")


@task_decorator(
    "GenerateBiotaApp", human_name="Generate Bio Navigator App", style=ReflexResource.copy_style()
)
class GenerateBiotaApp(Task):
    """
    Task that generates the Bio Navigator app.
    """

    input_specs = InputSpecs(
        {
            "app_config": InputSpec(
                File,
                human_name="App config file",
                short_description="The app config file to use",
            ),
        }
    )
    output_specs = OutputSpecs({"reflex_app": OutputSpec(ReflexResource)})

    config_specs = ConfigSpecs(
        {
            "chat_app_name": StrParam(
                human_name="Chat app name",
                short_description="Name of the chat app. All conversations are associated to this chat name.",
            ),
            "show_config_page": BoolParam(
                human_name="Show config page",
                short_description="Show the config page",
                default_value=True,
            ),
        }
    )

    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        """Run the task"""

        reflex_app = ReflexResource()

        # add the config file to the reflex resource and set the configuration file path
        app_config_file: File = cast(File, inputs["app_config"])
        reflex_app.add_resource(app_config_file, create_new_resource=False)
        reflex_app.set_param("configuration_file_path", app_config_file.path)

        reflex_app.set_param("chat_app_name", params["chat_app_name"])
        reflex_app.set_param("show_config_page", params["show_config_page"])

        reflex_app.set_app_config(BiotaAppAppConfig())
        reflex_app.name = "Bio Navigator"

        return {"reflex_app": reflex_app}

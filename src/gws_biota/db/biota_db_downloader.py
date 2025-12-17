import os

from gws_core import (
    ConfigParams,
    ConfigSpecs,
    DbManagerService,
    DockerComposeStatus,
    DockerService,
    InputSpecs,
    JSONDict,
    OutputSpec,
    OutputSpecs,
    RegisterComposeOptionsRequestDTO,
    Settings,
    StrParam,
    Task,
    TaskInputs,
    TaskOutputs,
    task_decorator,
)

from gws_biota.db.biota_db_manager import BiotaDbManager


@task_decorator(
    unique_name="BiotaDbDownloader",
    human_name="Biota DB Downloader",
    short_description="Start the Biota MariaDB database using Docker Compose",
)
class BiotaDbDownloader(Task):
    """
    # Biota DB Downloader

    A task that starts the Biota MariaDB database using Docker Compose.

    ## Overview

    This task deploys and starts a MariaDB container with the Biota database using Docker Compose.
    It loads the docker-compose.yml configuration from the brick's db folder, validates parameters,
    and initiates the Docker Compose deployment through the Docker service.

    ## Input/Output

    - **Inputs**: None
    - **Output**: `JSONDict` resource containing the Docker Compose operation response

    ## Configuration Parameters

    | Parameter | Type | Required | Description |
    |-----------|------|----------|-------------|
    | `db_url` | StrParam | Yes | URL to download the Biota database from |

    ## Behavior

    1. **Load Configuration**: Reads the docker-compose.yml from the brick's db folder
    2. **Environment Handling**: Environment variables are managed externally
    3. **Deployment**: Starts the Docker Compose using the YAML configuration
    4. **Wait for Ready**: Waits for the database container to reach UP status
    5. **Response**: Returns a structured JSON response with deployment status

    ## Output Format

    The output JSONDict contains:
    - `status`: Current status of the Docker Compose (e.g., "UP")
    - `info`: Additional information about the compose status
    - `brick_name`: The brick name used for deployment
    - `unique_name`: The unique name assigned to this compose instance

    ## Exceptions

    - Docker service exceptions: May be raised during compose deployment
    - Exception: Raised if the Docker Compose does not reach UP status within the timeout period

    ## Notes

    - The docker-compose.yml file must exist at the relative path `docker-compose.yml`
    - Environment variables (BIOTA_DB_PASSWORD, BIOTA_DB_USER, etc.) are handled externally
    - The task waits up to 20 attempts for the database to be ready
    """

    CONTAINER_UNIQUE_NAME = "db"
    DOCKER_COMPOSE_FILE = "docker-compose.yml"
    SERVICE_NAME = "lab-biota-db"

    input_specs = InputSpecs({})
    output_specs = OutputSpecs(
        {
            "response": OutputSpec(
                JSONDict,
                human_name="Docker Compose Response",
                short_description="Response from Docker Compose start operation",
            )
        }
    )

    config_specs = ConfigSpecs(
        {
            "db_url": StrParam(
                human_name="Database URL",
                short_description="URL to download the Biota database from",
                optional=True,
            ),
        }
    )

    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        brick_name = self.get_brick_name()
        unique_name = self.CONTAINER_UNIQUE_NAME
        db_url: str = params.get_value("db_url")

        if not db_url:
            self.log_info_message(
                f"Database URL is not provided, using default from settings : {db_url}"
            )
            db_url = Settings.get_instance().get_and_check_variable(
                self.get_brick_name(), "BIOTA_DB_URL"
            )

        # Load the docker-compose.yml file from the same directory as this task file
        task_file_dir = os.path.dirname(os.path.abspath(__file__))
        docker_compose_path = os.path.join(task_file_dir, self.DOCKER_COMPOSE_FILE)

        # Read the YAML content
        with open(docker_compose_path) as f:
            yaml_config = f.read()

        # Start the Docker Compose (environment is handled externally)
        docker_service = DockerService()

        db_config = BiotaDbManager.get_instance().get_prod_db_config()

        docker_service.register_and_start_compose(
            brick_name=brick_name,
            unique_name=unique_name,
            compose_yaml_content=yaml_config,
            options=RegisterComposeOptionsRequestDTO(
                description="Biota MariaDB Database",
                environment_variables={
                    "BIOTA_DB_PASSWORD": db_config.password,
                    "BIOTA_DB_USER": db_config.user,
                    "BIOTA_DB_NAME": db_config.db_name,
                    "BIOTA_DB_URL": db_url,
                },
                auto_start=True,
            ),
        )

        self.log_info_message("Docker Compose started, waiting for ready status...")
        response = docker_service.wait_for_compose_status(
            brick_name=brick_name,
            unique_name=unique_name,
            max_attempts=20,
            message_dispatcher=self.message_dispatcher,
        )

        if response.composeStatus.status != DockerComposeStatus.UP:
            text = f"Docker Compose did not start successfully, status: {response.composeStatus.status.value}."
            if response.composeStatus.info:
                text += f" Info: {response.composeStatus.info}."
            raise Exception(text)

        self.log_info_message("Waiting for the Biota database to be ready...")
        docker_service.wait_for_service_healthy(
            brick_name=brick_name,
            unique_name=unique_name,
            service_name=self.SERVICE_NAME,
            interval_seconds=10,
            max_attempts=30,
            message_dispatcher=self.message_dispatcher,
        )
        self.log_info_message("Biota database is ready.")

        # Check Db Manager connection
        self.log_info_message("Verifying Biota database connection...")
        biota_db_manager = BiotaDbManager.get_instance()
        DbManagerService.init_db(biota_db_manager, full_init=True)
        if not biota_db_manager.check_connection():
            raise Exception("Failed to connect to the Biota database after download.")
        self.log_success_message("Successfully connected to the Biota database.")

        # Create JSON output
        json_dict = JSONDict()
        json_dict.data = {
            "status": response.composeStatus.status.value,
            "info": response.composeStatus.info,
            "brick_name": brick_name,
            "unique_name": unique_name,
        }

        return {"response": json_dict}

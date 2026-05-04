import os

from gws_core import (
    ConfigParams,
    ConfigSpecs,
    DockerService,
    File,
    InputSpecs,
    OutputSpec,
    OutputSpecs,
    Task,
    TaskInputs,
    TaskOutputs,
    task_decorator,
)
from gws_core.core.utils.compress.zip_compress import ZipCompress

from gws_biota.db.biota_db_manager import BiotaDbManager


@task_decorator(
    unique_name="BiotaDbZipper",
    human_name="Biota DB Zipper",
    short_description="Export the Biota MariaDB data folder as a zip file",
)
class BiotaDbZipper(Task):
    """
    # Biota DB Zipper

    A task that zips the local Biota MariaDB data folder so it can be uploaded
    to the cloud S3 bucket to declare a new version of the Biota database.

    ## Overview

    The Biota database is hosted in a MariaDB Docker container whose data
    directory (`/var/lib/mysql`) is mounted on the host through the
    `LAB_VOLUME_HOST_NO_BACKUP` volume defined in
    `gws_biota/db/docker-compose.yml`. This task locates the host directory
    backing that volume via `DockerService.get_volume_local_path` (with
    `include_in_backup=False`) and creates a zip archive of its content.

    This replaces the manual `prepare_db.sh` script previously executed inside
    the database Docker container.

    ## Input/Output

    - **Inputs**: None
    - **Output**: `File` resource pointing to the generated zip archive

    ## Notes

    - The Biota DB Docker compose must have been registered (e.g. via
      `BiotaDbDownloader`) so that the host volume exists.
    - For consistency, it is recommended to stop the database container before
      running this task to avoid zipping data while MariaDB is writing to disk.
    """

    input_specs = InputSpecs({})
    output_specs = OutputSpecs(
        {
            "zip_file": OutputSpec(
                File,
                human_name="Biota DB zip",
                short_description="Zip archive of the Biota MariaDB data folder",
            )
        }
    )

    config_specs = ConfigSpecs({})

    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        brick_name = self.get_brick_name()
        unique_name = BiotaDbManager.get_instance().get_name()

        docker_service = DockerService()
        db_folder_path = docker_service.get_volume_local_path(
            brick_name=brick_name,
            unique_name=unique_name,
            include_in_backup=False,
        )

        if not os.path.isdir(db_folder_path):
            raise Exception(
                f"Biota DB volume folder does not exist at '{db_folder_path}'. "
                "Make sure the Biota DB Docker compose has been registered."
            )

        self.log_info_message(f"Zipping Biota DB folder '{db_folder_path}'...")

        tmp_dir = self.create_tmp_dir()
        zip_file_path = os.path.join(tmp_dir, "biota_db.zip")

        ZipCompress.compress_dir(db_folder_path, zip_file_path)

        self.log_success_message(f"Biota DB folder zipped to '{zip_file_path}'.")

        return {"zip_file": File(zip_file_path)}

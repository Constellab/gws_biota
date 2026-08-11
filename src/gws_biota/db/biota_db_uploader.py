from gws_core import (
    ConfigParams,
    ConfigSpecs,
    CredentialsDataS3,
    CredentialsParam,
    File,
    InputSpec,
    InputSpecs,
    OutputSpecs,
    S3Bucket,
    StrParam,
    Task,
    TaskInputs,
    TaskOutputs,
    task_decorator,
)


@task_decorator(
    unique_name="BiotaDbUploader",
    human_name="Biota DB Uploader",
    short_description="Upload a Biota DB zip to the cloud bucket to declare a new DB version",
)
class BiotaDbUploader(Task):
    """
    # Biota DB Uploader

    A task that uploads a zipped Biota MariaDB data folder to the cloud bucket,
    to declare a new version of the Biota database.

    ## Overview

    This is the missing step between `BiotaDbZipper` (which produces the zip) and
    `BiotaDbDownloader` (which consumes it). It uploads the zip **as a raw file**,
    under a versioned key:

    ```
    db/<db_version>/mariadb.zip
    ```

    Unlike the generic `ResourceUploaderS3` task from `gws_core`, the uploaded
    object is the zip itself, byte for byte. `ResourceUploaderS3` wraps its input
    in a `ResourceZipper` archive named `<uuid>.tar`, which is meant to be re-imported
    by another data lab and cannot be consumed by the Biota DB Docker image.

    Once uploaded, update the `BIOTA_DB_URL` variable in the brick `settings.json`
    to point to the new key, so that `BiotaDbDownloader` picks up the new version.

    ## Input/Output

    - **Input**: `File` resource, the zip produced by `BiotaDbZipper`
    - **Outputs**: None

    ## Configuration Parameters

    | Parameter | Type | Required | Description |
    |-----------|------|----------|-------------|
    | `credentials` | CredentialsParam (S3) | Yes | S3 credentials of the storage account |
    | `bucket` | StrParam | Yes | Target bucket, defaults to `gws-biota` |
    | `db_version` | StrParam | Yes | Version of the DB, e.g. `0.14.0`, used to build the object key |

    ## Notes

    - **Bucket naming**: the historical `gws_biota` container cannot be used here, which is
      why the default is `gws-biota` (hyphen). Swift container names may contain
      underscores, S3 bucket names may not, so the OVH S3 gateway answers
      `400 InvalidBucketName` for `gws_biota` and omits it from `ListBuckets` entirely. That
      container is fine, it is simply not addressable over S3, whatever the endpoint or
      credentials. `gws-biota` lives in the same Swift account and is public.
    - **Public read**: `database_image/init-db.sh` downloads the zip with an anonymous
      `wget`, so the uploaded object must be publicly readable. Note that the S3 host
      itself refuses anonymous requests: the public URL is the Swift one,
      `https://storage.<region>.cloud.ovh.net/v1/AUTH_<project>/<container>/<key>`.
    - **Zip layout**: `init-db.sh` extracts the archive and copies `/tmp/mariadb/*`, so
      the zip must contain a top-level `mariadb/` folder.
    """

    OBJECT_ROOT_FOLDER = "db"
    OBJECT_FILE_NAME = "mariadb.zip"

    input_specs = InputSpecs(
        {
            "zip_file": InputSpec(
                File,
                human_name="Biota DB zip",
                short_description="Zip archive of the Biota MariaDB data folder",
            )
        }
    )
    output_specs = OutputSpecs({})

    config_specs = ConfigSpecs(
        {
            "credentials": CredentialsParam(
                credentials_type=CredentialsDataS3,
                human_name="S3 credentials",
                short_description="Credentials of the storage account hosting the Biota DB",
            ),
            "bucket": StrParam(
                human_name="Bucket",
                short_description="Name of the bucket to upload the Biota DB to",
                default_value="gws-biota",
            ),
            "db_version": StrParam(
                human_name="DB version",
                short_description="Version of the Biota DB, used as folder name (e.g. 0.14.0)",
            ),
        }
    )

    def run(self, params: ConfigParams, inputs: TaskInputs) -> TaskOutputs:
        zip_file: File = inputs["zip_file"]

        credentials: CredentialsDataS3 = params.get_value("credentials")
        bucket_name: str = params.get_value("bucket")
        db_version: str = params.get_value("db_version").strip("/")

        # Warn rather than raise: the name may be valid for another protocol (Swift
        # containers do allow underscores), but the S3 API will reject it.
        if bucket_name != bucket_name.lower() or "_" in bucket_name:
            self.log_warning_message(
                f"Bucket '{bucket_name}' is not a valid S3 bucket name (S3 requires lowercase "
                "names without underscores). The upload will fail unless the storage is reached "
                "through another API. Use an S3-legal bucket name instead."
            )

        object_key = f"{self.OBJECT_ROOT_FOLDER}/{db_version}/{self.OBJECT_FILE_NAME}"

        s3_bucket = S3Bucket(
            endpoint=credentials.endpoint_url,
            region=credentials.region,
            access_key_id=credentials.access_key_id,
            secret_access_key=credentials.secret_access_key,
            bucket_name=bucket_name,
            # forward the dispatcher to report the upload progress, the Biota DB zip
            # weighs a couple of GB
            message_dispatcher=self.message_dispatcher,
        )

        self.log_info_message(f"Uploading Biota DB version '{db_version}' to '{bucket_name}'")

        s3_bucket.upload_file(zip_file.path, object_key)

        # The S3 host answers 401 to anonymous requests, so it is not the download URL.
        # Public reads go through the Swift URL of the container, which is what
        # BIOTA_DB_URL must point to for init-db.sh to wget the archive.
        self.log_success_message(
            f"Biota DB uploaded to '{bucket_name}/{object_key}'. Set BIOTA_DB_URL in the brick "
            f"settings.json to the public Swift URL of the container, "
            f"i.e. https://storage.<region>.cloud.ovh.net/v1/AUTH_<project>/{bucket_name}/{object_key}"
        )

        return {}

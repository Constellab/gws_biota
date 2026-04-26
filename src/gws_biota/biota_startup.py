import subprocess

from gws_core import (
    AuthenticateUser,
    BrickLogService,
    DbManagerService,
    Event,
    EventListener,
    Logger,
    ScenarioProxy,
    Settings,
    event_listener,
)

from gws_biota.db.biota_db_downloader import BiotaDbDownloader
from gws_biota.db.biota_db_manager import BiotaDbManager


@event_listener
class GwsCoreDbListener(EventListener):
    """
    Listen to gws_core event to sync user database.

    Args:
        EventListener (_type_): _description_
    """

    def handle(self, event: Event) -> None:
        if event.type == "system" and event.action == "started":
            self._ensure_system_dependencies()
            self.init_database()

    def _ensure_system_dependencies(self) -> None:
        """Install required system packages if not already present.

        pigz is used by gws_core's tar decompressor (tar_compress.py) and must
        be available in any environment running taxonomy/enzyme db imports.
        """
        try:
            result = subprocess.run(["which", "pigz"], capture_output=True)
            if result.returncode != 0:
                Logger.info("pigz not found — installing via apt-get...")
                subprocess.run(
                    ["apt-get", "install", "-y", "--no-install-recommends", "pigz"],
                    check=True, capture_output=True
                )
                Logger.info("✓ pigz installed successfully")
        except Exception as e:
            Logger.warning(f"Could not install pigz: {e}")

    def init_database(self) -> None:
        """Initialize the database"""
        biota_db_manager = BiotaDbManager.get_instance()

        initialized = DbManagerService.init_db(biota_db_manager, full_init=True)

        if not initialized:
            Logger.info("Biota database not initialized, installing database")
            result = self._install_database()
            if not result:
                return

        if not biota_db_manager.check_connection():
            BrickLogService.log_brick_critical(
                BiotaDbManager, "Biota database not initialized properly."
            )
            return

    def _install_database(self) -> bool:
        """Install the database"""

        if Settings.is_dev_mode():
            BrickLogService.log_brick_critical(
                BiotaDbManager,
                "Dev mode detected, skipping Biota database installation. The biota database must be installed in the production environment because it is common for both environments. Please add the 'gws_biota' brick to your datalab.",
            )
            return True

        with AuthenticateUser.system_user():
            scenario_proxy = ScenarioProxy(title="Biota Database Installation")
            scenario_proxy.get_protocol().add_process(BiotaDbDownloader)
            try:
                BrickLogService.log_brick_info(
                    BiotaDbManager,
                    f"Starting Biota database installation in scenario '{scenario_proxy.get_url()}'",
                )
                scenario_proxy.run()
            except Exception as e:
                BrickLogService.log_brick_critical(
                    BiotaDbManager,
                    f"Error while installing Biota database: {e}. Check scenario '{scenario_proxy.get_url()}' for details.",
                )
                return False

        try:
            biota_db_manager = BiotaDbManager.get_instance()
            DbManagerService.init_db(biota_db_manager, full_init=True)
        except Exception as e:
            BrickLogService.log_brick_critical(
                BiotaDbManager, f"Error while initializing Biota database: {e}"
            )
            return False

        BrickLogService.log_brick_info(BiotaDbManager, "Biota database installation completed.")
        return True

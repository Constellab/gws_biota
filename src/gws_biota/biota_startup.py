from gws_biota.db.biota_db_downloader import BiotaDbDownloader
from gws_biota.db.biota_db_manager import BiotaDbManager
from gws_core import (
    Event,
    EventListener,
    event_listener,
    DbManagerService,
    Logger,
    ScenarioProxy,
    BrickService,
    AuthenticateUser,
    Settings,
)


@event_listener
class GwsCoreDbListener(EventListener):
    """
    Listen to gws_core event to sync user database.

    Args:
        EventListener (_type_): _description_
    """

    def handle(self, event: Event) -> None:
        if event.type == "system" and event.action == "started":
            self.init_database()

    def init_database(self) -> None:
        """Initialize the database"""
        biota_db_manager = BiotaDbManager.get_instance()

        initialized = DbManagerService.init_db(
            biota_db_manager, full_init=True, ignore_error=True
        )

        if not initialized:
            Logger.info("Biota database not initialized, installing database")
            result = self._install_database()
            if not result:
                return

        if not biota_db_manager.check_connection():
            BrickService.log_brick_critical(
                BiotaDbManager, "Biota database not initialized properly."
            )
            return

    def _install_database(self) -> bool:
        """Install the database"""

        if Settings.is_dev_mode():
            BrickService.log_brick_critical(
                BiotaDbManager,
                "Dev mode detected, skipping Biota database installation. The biota database must be installed in the production environment because it is common for both environments. Please add the 'gws_biota' brick to your datalab.",
            )
            return True

        with AuthenticateUser.system_user():
            scenario_proxy = ScenarioProxy(title="Biota Database Installation")
            scenario_proxy.get_protocol().add_process(BiotaDbDownloader)
            try:
                BrickService.log_brick_info(
                    BiotaDbManager,
                    f"Starting Biota database installation in scenario '{scenario_proxy.get_url()}'",
                )
                scenario_proxy.run()
            except Exception as e:
                BrickService.log_brick_critical(
                    BiotaDbManager,
                    f"Error while installing Biota database: {e}. Check scenario '{scenario_proxy.get_url()}' for details.",
                )
                return False

        try:
            biota_db_manager = BiotaDbManager.get_instance()
            DbManagerService.init_db(biota_db_manager, full_init=True)
        except Exception as e:
            BrickService.log_brick_critical(
                BiotaDbManager, f"Error while initializing Biota database: {e}"
            )
            return False

        BrickService.log_brick_info(
            BiotaDbManager, "Biota database installation completed."
        )
        return True

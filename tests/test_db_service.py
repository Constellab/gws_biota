import time

from gws_core import Settings, GTest, Experiment, BaseTestCase, ExperimentService
from gws_biota.db.db_service import DbService, DbCreator, QueueService

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestDbService(BaseTestCase):

    def test_db_service_status(self):
        self.print("DbService status")
        self.assertTrue(DbService.is_ready())
        self.assertTrue(not DbService.is_busy())

    async def test_build_biota(self):
        self.print("Build biota")
        
        experiment = DbService.build_biota_db()
        
        print("Wating 10 sec for the experiment to start ...")
        time.sleep(5)
        experiment.refresh()
        self.assertTrue(experiment.pid > 0)        
 
        print("Wating 10 sec before killing experiment ...")
        time.sleep(10)
        ExperimentService.stop_experiment(uri=experiment.uri)
        experiment.refresh()
        self.assertFalse(experiment.is_running)
        self.assertTrue(experiment.pid == 0)        
        time.sleep(5)
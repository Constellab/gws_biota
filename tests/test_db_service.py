import sys
import os
from unittest import IsolatedAsyncioTestCase
import time

from gws_core import Settings, GTest, Experiment, ExperimentService
from gws_biota.service.db_service import DbService
from gws_biota.proc.db_creator import DbCreator

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestDbService(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        GTest.drop_tables()
        GTest.create_tables()
        GTest.init()

    @classmethod
    def tearDownClass(cls):
        GTest.drop_tables()

    def test_db_service_status(self):
        GTest.print("DbService status")
        self.assertTrue(DbService.is_ready())
        self.assertTrue(not DbService.is_busy())

    async def test_build_biota(self):
        return
        GTest.print("Build biota")

        #e = DbService.build_biota_db(user=GTest.user)
        db_creator = DbCreator()
        experiment: Experiment = ExperimentService.create_experiment_from_process(process=db_creator)
        experiment = await ExperimentService.run_experiment(
            experiment=experiment, user=GTest.user)

        e.set_title("Creation of biota database")
        e.run_through_cli(user=GTest.user)
        self.assertTrue(e.is_running)
        self.assertTrue(e.pid > 0)        
 
        print("Wating 10 sec before killing experiment ...")
        time.sleep(10)
        
        e.kill_pid_through_cli()
        e.refresh()
        self.assertFalse(e.is_running)
        self.assertTrue(e.pid == 0)        
        
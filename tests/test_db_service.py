import time

from gws_core import Settings, GTest, Experiment, ExperimentService, BaseTestCase, ProcessService, ProcessModel, Study
from gws_biota.db.db_service import DbService
from gws_biota.db.db_creator import DbCreator

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestDbService(BaseTestCase):

    def test_db_service_status(self):
        GTest.print("DbService status")
        self.assertTrue(DbService.is_ready())
        self.assertTrue(not DbService.is_busy())

    async def test_build_biota(self):
        GTest.print("Build biota")

        db_creator_model: ProcessModel = ProcessService.create_process_model_from_type(process_type=DbCreator)
        experiment: Experiment = ExperimentService.create_experiment_from_process_model(
            process_model=db_creator_model, 
            study=Study.get_default_instance()
        )
        experiment = await ExperimentService.run_experiment(
            experiment=experiment, 
            user=GTest.user
        )

        experiment.set_title("Creation of biota database")
        experiment.run_through_cli(user=GTest.user)
        self.assertTrue(experiment.is_running)
        self.assertTrue(experiment.pid > 0)        
 
        print("Wating 10 sec before killing experiment ...")
        time.sleep(10)
        
        experiment.kill_pid_through_cli()
        experiment.refresh()
        self.assertFalse(experiment.is_running)
        self.assertTrue(experiment.pid == 0)        
        
import time

from gws_core import Settings, GTest, ExperimentService, Experiment, BaseTestCase, TaskService, TaskModel, Study
from gws_biota.db.db_service import DbService
from gws_biota.db.db_creator import DbCreator

settings = Settings.retrieve()
testdata_path = settings.get_variable("gws_biota:testdata_dir")

class TestDbService(BaseTestCase):

    def test_db_service_status(self):
        self.print("DbService status")
        self.assertTrue(DbService.is_ready())
        self.assertTrue(not DbService.is_busy())

    async def test_build_biota(self):
        self.print("Build biota")

        db_creator_model: TaskModel = TaskService.create_task_model_from_type(task_type=DbCreator)
        experiment: Experiment = ExperimentService.create_experiment_from_task_model(
            task_model=db_creator_model
        )
        ExperimentService.run_through_cli(
            experiment=experiment, 
            user=GTest.user
        )

        self.assertTrue(experiment.is_running)
        self.assertTrue(experiment.pid > 0)        
 
        print("Wating 10 sec before killing experiment ...")
        time.sleep(10)
        ExperimentService.stop_experiment(uri=experiment.uri)
        experiment.refresh()
        self.assertFalse(experiment.is_running)
        self.assertTrue(experiment.pid == 0)        
        time.sleep(5)
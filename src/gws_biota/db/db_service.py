# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

from gws_core import (BadRequestException, BaseService, CurrentUserService,
                      Experiment, ExperimentService, Job, MySQLBase,
                      MySQLService, Protocol, Queue, QueueService, Requests,
                      Settings, TaskModel, TaskService, UserService)

from .db_creator import DbCreator


class DbService(BaseService):

    @classmethod
    def build_biota_db(cls, user=None) -> Experiment:
        """
        Build biota db
        """

        if not user:
            user = UserService.get_sysuser()
            user.save()
            CurrentUserService.set_current_user(user)

        db_creator_model: TaskModel = TaskService.create_task_model_from_type(task_type=DbCreator)
        experiment: Experiment = ExperimentService.create_experiment_from_task_model(
            task_model=db_creator_model
        )
        experiment.save()
        try:
            QueueService.add_experiment_to_queue(
                experiment_id=experiment.id)
        except Exception as err:
            raise BadRequestException(f"An error occured while adding the experiment to the job queue") from err

        experiment.refresh()
        return experiment

    @classmethod
    def dump_biota_db(cls) -> bool:
        MySQLService.dump_db("biota", force=True, wait=False)
        return True

    @classmethod
    def is_busy(cls) -> bool:
        base = MySQLBase()
        base.set_default_config("biota")
        return not base.is_ready()

    @classmethod
    def is_ready(cls) -> bool:
        base = MySQLBase()
        base.set_default_config("biota")
        return base.is_ready()

    @classmethod
    def load_biota_db(cls) -> bool:
        MySQLService.load_db("biota", force=True, wait=True)
        return True

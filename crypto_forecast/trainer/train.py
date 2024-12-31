import os

import mlflow

from utils.logger import setup_logger

LOGGER = setup_logger(__name__, 'train_workflow.log')


def setup_experiment(experiment_name, artifact_location):

    try:
        mlflow.create_experiment(
            experiment_name, 
            artifact_location=artifact_location
        )

        LOGGER.info(
            f"🧪 Experiment {experiment_name} is not Exist.\
            Create Experiment."
        )
    except:
        LOGGER.info(
            f"🧪 Experienmt {experiment_name} is Already Exist.\
            Execute Run on the \"{experiment_name}\"."
        )
            
    # set experiment
    mlflow.set_experiment(experiment_name)

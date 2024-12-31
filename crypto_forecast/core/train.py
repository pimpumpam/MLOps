import os
import argparse

import mlflow

from trainer.train import setup_experiment
from utils.logger import setup_logger
from utils.utils import load_spec_from_config


LOGGER = setup_logger(__name__, 'train_workflow.log')

class Trainer:
    def __init__(self, cfg_meta, cfg_model, cfg_hyp):
        self.cfg_meta = cfg_meta
        self.cfg_model = cfg_model
        self.cfg_hyp = cfg_hyp

    def run(self, **kwargs):
        mlflow.set_tracking_uri(self.cfg_meta.mlflow['DASHBOARD_URL'])

        # set experiment
        setup_experiment(
            self.cfg_meta.exp_name,
            artifact_location=self.cfg_meta.mlflow['ARTIFACT_DIR']
        )

        # set run
        with mlflow.start_run(run_name=self.cfg_model.name) as run:
            
            # train code
            print("학습 코드 개발 진행 중")



if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument('--config', type=str, default='dlinear', help="Config 파이썬 파일 명. 확장자는 제외.")
    args = parser.parse_args()

    # configs
    (
        cfg_meta, 
        _, # cfg_loader 
        _, # cfg_preprocessor
        cfg_model,
        cfg_hyp, 
        _  # cfg_evaluate
    ) = load_spec_from_config(args.config)

    # train
    learner = Trainer(cfg_meta, cfg_model, cfg_hyp)
    learner.run()
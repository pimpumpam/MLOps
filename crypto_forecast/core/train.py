import os
import argparse

import mlflow

from trainer.train import setup_experiment, train

from utils.logger import setup_logger
from utils.utils import load_spec_from_config, hyperparameter_combination


LOGGER = setup_logger(__name__, 'train_workflow.log')

class Trainer:
    def __init__(self, cfg_meta, cfg_model, cfg_hyp):
        self.cfg_meta = cfg_meta
        self.cfg_model = cfg_model
        self.cfg_hyp = cfg_hyp

    def run(self, dataset):
        # 학습 & 검증 데이터 DB에서 불러오기
        
        
        mlflow.set_tracking_uri(self.cfg_meta.mlflow['DASHBOARD_URL'])

        # set experiment
        setup_experiment(
            self.cfg_meta.exp_name,
            artifact_location=self.cfg_meta.mlflow['ARTIFACT_DIR']
        )


        # set hyperparameter
        hyp_list = hyperparameter_combination(self.cfg_hyp)
        
        # set run
        with mlflow.start_run(run_name=self.cfg_model.name) as run:
            
            # train code
            if len(hyp_list)>1:
                LOGGER.info("Hyperparmaeter optimization process need to be developed")
                
            else:
                hyp = hyp_list.pop()
                
                train(
                    dataset=dataset,
                    model='개발필요',
                    batch_size=hyp_list['batch_size'],
                    num_epochs=hyp_list['num_epochs'],
                    learning_rate=hyp_list['learning_rate'],
                    device='cpu'
                )


if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument('--config', type=str, default='dlinear', help="Config 파이썬 파일 명. 확장자는 제외.")
    args = parser.parse_args()

    # configs
    (
        cfg_meta,
        _, # cfg_database
        _, # cfg_loader
        _, # cfg_preprocessor
        cfg_model,
        cfg_hyp,
        _, # cfg_evaluate
    ) = load_spec_from_config('dlinear')

    # train
    learner = Trainer(cfg_meta, cfg_model, cfg_hyp)
    learner.run()
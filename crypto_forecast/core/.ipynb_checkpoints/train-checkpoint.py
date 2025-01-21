import os
import sys
import json
import argparse
import collections
from pathlib import Path

import torch
import torch.multiprocessing as mp

import mlflow
from mlflow.models.signature import infer_signature

from models.model import Model
from trainer.train import setup_experiment, train
from preprocessor.data_preparation import split_sliding_window
from utils.logger import setup_logger
from utils.utils import load_spec_from_config, hyperparameter_combination

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
sys.path.append(str(ROOT))
from db_handler.database import SQLiteDBManager

LOGGER = setup_logger(__name__, 'train_workflow.log')


class Trainer:
    def __init__(self, cfg_meta, cfg_database, cfg_preprocessor, cfg_model, cfg_hyp, cfg_train):
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_preprocessor = cfg_preprocessor
        self.cfg_model = cfg_model
        self.cfg_hyp = cfg_hyp
        self.cfg_train = cfg_train
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)

    def run(self):
        
        RUN_IDs = collections.defaultdict(list)
        
        LOGGER.info("Read train dataset")
        print("Read Train Dataset")
        train_data = self.db_manager.fetch_to_dataframe(
            f"""
            SELECT *
            FROM {self.cfg_train.scheme}_{self.cfg_train.table}
            WHERE 1=1
                AND MARKET='KRW-BTC'
            ;
            """
        )
        
        LOGGER.info("Apply sliding window to train data")
        X_train, y_train = split_sliding_window(
            data = train_data,
            feature_col = self.cfg_train.field['feature'],
            input_seq_len = self.cfg_preprocessor.seq_len,
            label_seq_len = self.cfg_preprocessor.pred_len,
            time_col = 'KST_TIME'
        )
        
        # set experiment
        setup_experiment(
            self.cfg_meta.exp_name,
            artifact_location=self.cfg_meta.mlflow['ARTIFACT_DIR']
        )
        
        # set hyperparameter
        hyp_list = hyperparameter_combination(self.cfg_hyp)
        
        # set run
        with mlflow.start_run(run_name=self.cfg_model.name) as run:
            
            # model schema
            signature = infer_signature(X_train[0], y_train[0])
            
            # train code
            if len(hyp_list)>1:
                LOGGER.info("Hyperparameter Optimization")
                for idx, hyp in enumerate(hyp_list):
                    
                    model = Model(self.cfg_model)
                    
                    with mlflow.start_run(run_name=f"{self.cfg_model.name}_{str(idx+1)}", nested=True) as nested_run:
                        LOGGER.info(f"Initialize model training (Nested) | Exp: {self.cfg_meta.exp_name} | Run: {nested_run.info.run_id}")
                        train(
                            dataset = (X_train, y_train),
                            model = model,
                            batch_size = hyp['batch_size'],
                            num_epochs = hyp['num_epoch'],
                            learning_rate = hyp['learning_rate'],
                            device='cpu'
                        )
                        
                        mlflow.log_params(hyp)
                        mlflow.pytorch.log_model(
                            pytorch_model = model,
                            artifact_path = 'model',
                            signature=signature
                        )
                        
                        RUN_IDs['run_id'].append(nested_run.info.run_id)
                
            else:
                LOGGER.info(f"Initialize model training | Exp: {self.cfg_meta.exp_name} | Run: {run.info.run_id}")
                
                hyp = hyp_list.pop()
                model = Model(self.cfg_model)
                
                train(
                    dataset = (X_train, y_train),
                    model = model,
                    batch_size = hyp['batch_size'],
                    num_epochs = hyp['num_epoch'],
                    learning_rate = hyp['learning_rate'],
                    device = 'cpu'
                )
                
                mlflow.log_params(hyp)
                mlflow.pytorch.log_model(
                    pytorch_model = model,
                    artifact_path = 'model',
                    signature=signature
                )
                
                RUN_IDs['run_id'].append(run.info.run_id)
                
        with open(os.path.join(self.cfg_meta.project['STATIC_DIR'], 'run_ids.json'), 'w') as f:
            json.dump(RUN_IDs, f)
                

if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument('--config', type=str, default='dlinear', help="Config 파이썬 파일 명. 확장자는 제외.")
    args = parser.parse_args()

    # configs
    (
        cfg_meta,
        cfg_database,
        _, # cfg_loader
        cfg_preprocessor,
        cfg_model,
        cfg_hyp,
        cfg_train,
        _, # cfg_evaluate
    ) = load_spec_from_config('dlinear')

    # train
    learner = Trainer(cfg_meta, cfg_database, cfg_preprocessor, cfg_model, cfg_hyp, cfg_train)
    learner.run()
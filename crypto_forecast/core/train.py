import os
import argparse

import mlflow

from models.model import Model
from trainer.train import setup_experiment, train
from preprocessor.data_preparation import split_sliding_window

from utils.database import SQLiteDBManager
from utils.logger import setup_logger
from utils.utils import load_spec_from_config, hyperparameter_combination


LOGGER = setup_logger(__name__, 'train_workflow.log')

class Trainer:
    def __init__(self, cfg_meta, cfg_database, cfg_preprocessor, cfg_model, cfg_hyp):
        self.cfg_meta = cfg_meta
        self.cfg_preprocessor = cfg_preprocessor
        self.cfg_model = cfg_model
        self.cfg_hyp = cfg_hyp
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)

    def run(self):
        
        LOGGER.info("Read train dataset")
        train_data = self.db_manager.fetch_to_dataframe(
            """
            SELECT *
            FROM dw_gld_crypto_transc_candle_upbit_1min_train
            WHERE 1=1
                AND MARKET='KRW-BTC'
            ;
            """
        )
        
        LOGGER.info("Apply sliding window to train data")
        X_train, y_train = split_sliding_window(
            data = train_data,
            feature_col = self.cfg_preprocessor.feature_cols['gold'],
            input_seq_len = self.cfg_preprocessor.seq_len,
            label_seq_len = 1,
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
            
            # train code
            if len(hyp_list)>1:
                LOGGER.info("Hyperparmaeter optimization process need to be developed")
                
            else:
                hyp = hyp_list.pop()
                
                LOGGER.info("Train model")
                train(
                    dataset = (X_train, y_train),
                    model = Model(self.cfg_model),
                    batch_size = hyp_list['batch_size'],
                    num_epochs = hyp_list['num_epochs'],
                    learning_rate = hyp_list['learning_rate'],
                    device = 'cpu'
                )


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
        _, # cfg_evaluate
    ) = load_spec_from_config('dlinear')

    # train
    learner = Trainer(cfg_meta, cfg_database, cfg_preprocessor, cfg_model, cfg_hyp)
    learner.run()
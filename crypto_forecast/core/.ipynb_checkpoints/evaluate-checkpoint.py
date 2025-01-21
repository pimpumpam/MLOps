import os
import sys
import json
import pickle
import argparse
import numpy as np
import pandas as pd
from pathlib import Path

import torch

import mlflow

from preprocessor.transformation import MultiColumnScaler
from preprocessor.data_preparation import split_sliding_window
from evaluator.evaluate import evaluate
from utils.metrics import mean_absolute_error, root_mean_square_error, mean_absolute_percentage_error
from utils.logger import setup_logger

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
sys.path.append(str(ROOT))
from db_handler.database import SQLiteDBManager


LOGGER = setup_logger(__name__, 'train_workflow.log')

class Evaluator:
    
    def __init__(self, cfg_meta, cfg_database, cfg_preprocessor, cfg_evaluate):
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_evaluate = cfg_evaluate
        self.cfg_preprocessor = cfg_preprocessor
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
        
    def run(self):
        
        # [ LOAD OBJECT ]
        # load run-id info
        with open(os.path.join(self.cfg_meta.project['STATIC_DIR'], 'run_ids.json'), 'r') as f:
            RUN_IDs = json.load(f)
        RUN_IDs = RUN_IDs['run_id']
        
        # load scaler
        LOGGER.info("Load Scaler Object")
        scaler = MultiColumnScaler(self.cfg_preprocessor.transform['SCALER']['name'])
        with open(
            os.path.join(
                self.cfg_preprocessor.transform['SCALER']['save_dir'],
                f"{self.cfg_preprocessor.transform['SCALER']['name']}_{self.cfg_preprocessor.transform['SCALER']['save_name']}.pkl"
            ),
            'rb'
        ) as r:
            scaler_dict = pickle.load(r)
        scaler.scaler_dict = scaler_dict
        
        
        # [ LOAD DATA ]
        # load data
        LOGGER.info("Read test dataset")
        test_data = self.db_manager.fetch_to_dataframe(
            f"""
            SELECT *
            FROM {self.cfg_evaluate.scheme}_{self.cfg_evaluate.table}
            WHERE 1=1
                AND MARKET='KRW-BTC'
            ;    
            """
        )        
        
        # [ TRANSFORM DATA ]
        # apply sliding window
        LOGGER.info("Apply sliding window to test data")
        X, y = split_sliding_window(
            data = test_data,
            feature_col = self.cfg_evaluate.field['feature'],
            input_seq_len = self.cfg_preprocessor.seq_len,
            label_seq_len = self.cfg_preprocessor.pred_len,
            time_col = 'KST_TIME'
        )
        
        
        # [ EVALUATE ]
        # evaluate trained model
        for run_id in RUN_IDs:
            LOGGER.info(f"Evaluate trained model | Exp: {self.cfg_meta.exp_name} | Run: {run_id}")
            with mlflow.start_run(run_id=run_id) as run:
                
                hyp = mlflow.get_run(run_id).data.params
                model = mlflow.pytorch.load_model(
                    model_uri=os.path.join(
                        self.cfg_meta.mlflow['ARTIFACT_DIR'],
                        run_id,
                        'artifacts',
                        'model'
                    )
                )
                
                # evaluating
                pred, truth = evaluate(
                    dataset = (X, y),
                    model = model,
                    batch_size = int(hyp['batch_size']),
                    device = 'cpu'
                )                
                        
                # post processing
                LOGGER.info(f"Inverse transformation for predicted result")
                pred = np.array(pred).reshape(-1, len(self.cfg_evaluate.field['label']))
                truth = np.array(truth).reshape(-1, len(self.cfg_evaluate.field['label']))
                
                pred = pd.DataFrame(pred, columns=self.cfg_evaluate.field['label'])
                truth = pd.DataFrame(truth, columns=self.cfg_evaluate.field['label'])
                
                
                scaler.inverse_transform(
                    data=pred,
                    columns=self.cfg_evaluate.field['label'],
                    inplace=True
                )

                scaler.inverse_transform(
                    data=truth,
                    columns=self.cfg_evaluate.field['label'],
                    inplace=True
                )
                
                # log metrics
                LOGGER.info(f"Logging model performence")
                mlflow.log_metrics({
                    'RMSE': root_mean_square_error(pred, truth),
                    'MAE': mean_absolute_error(pred, truth),
                    'MAPE': mean_absolute_percentage_error(pred, truth)
                })
                                            
import os
import pickle
import argparse
import pandas as pd

import mlflow

from preprocessor.transformation import MultiColumnScaler
from preprocessor.data_preparation import split_sliding_window
from evaluator.evaluate import evaluate
from utils.metrics import mean_absolute_error, root_mean_square_error, mean_absolute_percentage_error
from utils.database import SQLiteDBManager
from utils.logger import setup_logger

LOGGER = setup_logger(__name__, 'train_workflow.log')


RUN_ID = '97c7d2ab396d461bb8d4e2351668ffe3'

class Evaluator:
    
    def __init__(self, cfg_meta, cfg_database, cfg_preprocessor, cfg_evaluate):
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_evaluate = cfg_evaluate
        self.cfg_preprocessor = cfg_preprocessor
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
        
    def run(self):
        
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
        
        LOGGER.info("Apply sliding window to test data")
        X_test, y_test = split_sliding_window(
            data = test_data,
            feature_col = self.cfg_evaluate.field['feature'],
            input_seq_len = self.cfg_preprocessor.seq_len,
            label_seq_len = 1,
            time_col = 'KST_TIME'
        )
        
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
            
        if self.exist_child_run(RUN_ID):
            LOGGER.info(f"Initialize model evaluating (Nested)")
            for run_id in self.get_child_run_id(RUN_ID):
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
                            
                    pred, truth = evaluate(
                        dataset = (X_test, y_test),
                        model = model,
                        batch_size = int(hyp['batch_size']),
                        device = 'cpu'
                    )
                    
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
                    
                    mlflow.log_metrics({
                        'RMSE': root_mean_square_error(pred, truth),
                        'MAE': mean_absolute_error(pred, truth),
                        'MAPE': mean_absolute_percentage_error(pred, truth)
                    })
                                
        else:
            LOGGER.info(f"Initialize model evaluating")
            with mlflow.start_run(run_id=RUN_ID) as run:
                
                hyp = mlflow.get_run(RUN_ID).data.params
                model = mlflow.pytorch.load_model(
                    model_uri=os.path.join(
                        self.cfg_meta.mlflow['ARTIFACT_DIR'],
                        RUN_ID,
                        'artifacts',
                        'model'
                    )
                )
                        
                pred, truth = evaluate(
                    dataset = (X_test, y_test),
                    model = model,
                    batch_size = int(hyp['batch_size']),
                    device = 'cpu'
                )
                
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
                
                mlflow.log_metrics({
                    'RMSE': root_mean_square_error(pred, truth),
                    'MAE': mean_absolute_error(pred, truth),
                    'MAPE': mean_absolute_percentage_error(pred, truth)
                })
            
            
    @staticmethod
    def exist_child_run(run_id):
        """
        특정 run 하위에 child run이 존재하는지 여부 확인
        
        parameter
        ----------
        run_id(str): 일반 run 혹은 parent run의 ID
        
        return
        ----------
        (bool): Child run이 존재하면 True, 존재하지 않으면 False
        
        """
        
        run_info = mlflow.get_run(run_id)
        experiment_id = run_info.info.experiment_id
        
        child_run = mlflow.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"tags.mlflow.parentRunId = '{run_id}'"
        )
        
        return True if len(child_run)>0 else False
    
    
    @staticmethod
    def get_child_run_id(run_id):
        """
        Parent run 하위의 child run ID 조회
        
        parameter
        ----------
        run_id(str): Parent run의 ID
        
        return
        ----------
        (list): Child run의 ID로 구성 된 리스트
        
        """
            
        run_info = mlflow.get_run(run_id)
        experiment_id = run_info.info.experiment_id
        
        child_run = mlflow.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"tags.mlflow.parentRunId = '{run_id}'"
        )
        
        return child_run['run_id'].to_list()

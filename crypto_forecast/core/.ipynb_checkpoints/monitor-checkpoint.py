import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

import mlflow

from utils.logger import setup_logger
from utils.metrics import root_mean_square_error, mean_absolute_error, mean_absolute_percentage_error

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
sys.path.append(str(ROOT))
from db_handler.query import Query
from db_handler.database import SQLiteDBManager
from service.utils.experiment_tracker import tracking_experiment, tracking_run

LOGGER = setup_logger(__name__, 'train_workflow.log')

class Monitor:
    
    def __init__(self, cfg_meta, cfg_database, cfg_inference):
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_inference = cfg_inference
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
    def run(self):
        
        CRITERIA = 'RMSE' # RMSE, MAE, MAPE
        
        # registered model performance
        registered_models = mlflow.search_registered_models(
            filter_string = f"name = '{self.cfg_meta.model_name}'"
        ).pop()
        
        production_model_info = [model_info \
                                 for model_info in registered_models.latest_versions \
                                 if model_info.current_stage=='Production'].pop()
        
        exp_info = tracking_experiment(experiment_name=self.cfg_meta.exp_name)
        run_info = tracking_run(
            experiment_id=exp_info['experiment_id'],
            run_id=production_model_info.run_id
        ).pop()
        
        
        # [LOAD DATA]
        # load bronze and inference data
        LOGGER.info("Load data for monitoring")
        base_time = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        tic = datetime.strftime(base_time, '%Y-%m-%dT%H:%M:%S')
        toc = datetime.strftime(
            base_time.replace(minute=59, second=59, microsecond=0),
            "%Y-%m-%dT%H:%M:%S"
        )
        
        bronze_data = self.db_manager.fetch_to_dataframe(
            f"""
            SELECT KST_TIME, LOW_PRICE, HIGH_PRICE, OPEN_PRICE, CLOSE_PRICE
            FROM dw_brz_crypto_transc_candle_upbit_minutes
            WHERE 1=1
                AND MARKET = 'KRW-BTC'
                AND KST_TIME BETWEEN '{tic}' AND '{toc}'
            ;
            """
        ).drop_duplicates(subset=['KST_TIME']).sort_values('KST_TIME')
        bronze_data['KST_TIME'] = bronze_data['KST_TIME'].apply(lambda x: x.replace('T', ' '))
        
        
        infer_data = self.db_manager.fetch_to_dataframe(
            f"""
            SELECT KST_TIME, LOW_PRICE, HIGH_PRICE, OPEN_PRICE, CLOSE_PRICE
            FROM {self.cfg_inference.scheme}_{self.cfg_inference.table}
            WHERE 1=1
                AND ETL_TIME = '{datetime.strftime(base_time, '%Y-%m-%d %H:%M:%S')}'
            ;
            """
        ).drop_duplicates(subset=['KST_TIME']).sort_values('KST_TIME')
        
        # inference performance
        LOGGER.info("Log metric from inference result")
        truth = bronze_data[self.cfg_inference.field['label']].values
        pred = infer_data[self.cfg_inference.field['label']].values        
        
        metrics = {
            'RMSE': root_mean_square_error(pred, truth),
            'MAE': mean_absolute_error(pred, truth),
            'MAPE': mean_absolute_percentage_error(pred, truth)
        }
        
        if metrics[CRITERIA] < run_info[f'metrics.{CRITERIA}']:
            # 등록된 모델의 error가 더 큰 경우
            LOGGER.info(f"Model Need To Be UPDATED | Model Performance: {run_info[f'metrics.{CRITERIA}']} | Inference Performance: {metrics[CRITERIA]}")
            
            return 'update'
            
        else:
            LOGGER.info(f"Model NOT Need To Be Updated")
            
            return 'maintain'
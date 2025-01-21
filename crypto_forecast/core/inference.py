import os
import sys
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

import mlflow

from preprocessor.transformation import MultiColumnScaler
from preprocessor.data_preparation import split_sliding_window
from evaluator.evaluate import evaluate
from utils.utils import gernerate_time_range
from utils.metrics import mean_absolute_error, root_mean_square_error, mean_absolute_percentage_error
from utils.logger import setup_logger

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
sys.path.append(str(ROOT))
from db_handler.query import Query
from db_handler.database import SQLiteDBManager

LOGGER = setup_logger(__name__, 'train_workflow.log')


class Inferer:
    
    def __init__(self, cfg_meta, cfg_database, cfg_preprocessor, cfg_evaluate, cfg_inference):
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_evaluate = cfg_evaluate
        self.cfg_inference = cfg_inference
        self.cfg_preprocessor = cfg_preprocessor
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
    def run(self):
        
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
        infer_data = self.db_manager.fetch_to_dataframe(
            f"""
            SELECT *
            FROM (
                SELECT *
                FROM dw_slv_crypto_transc_candle_upbit_1min
                WHERE 1=1
                    AND MARKET = 'KRW-BTC'
                ORDER BY KST_TIME DESC
                LIMIT {self.cfg_preprocessor.seq_len+self.cfg_preprocessor.pred_len}
            )
            ORDER BY KST_TIME ASC
            ;
            """
        )
        
        scaler.transform(
            data = infer_data,
            columns = self.cfg_inference.field['feature'],
            inplace = True
        )

        # [ TRANSFORM DATA ]
        # apply sliding window
        LOGGER.info("Apply sliding window to inference data")
        X, y = split_sliding_window(
            data=infer_data,
            feature_col=self.cfg_inference.field['feature'],
            input_seq_len=self.cfg_preprocessor.seq_len,
            label_seq_len=self.cfg_preprocessor.pred_len,
            time_col='KST_TIME'
        )
        
        # [ INFERENCE ]
        # load registered model from MLFlow
        LOGGER.info("Search latest production model ...")
        registered_models = mlflow.search_registered_models(
            filter_string = f"name = '{self.cfg_meta.model_name}'"
        ).pop()
        production_model_info = [model_info \
                                 for model_info in registered_models.latest_versions \
                                 if model_info.current_stage=='Production'].pop()
        
        LOGGER.info(f"Load model | Name: {self.cfg_meta.model_name} | Ver: {production_model_info.version}")
        model_uri = f"models:/{self.cfg_meta.model_name}/{int(production_model_info.version)}"
        model = mlflow.pytorch.load_model(model_uri)
        hyp = mlflow.get_run(production_model_info.run_id).data.params
                
        # inferencing
        LOGGER.info(f"Predict for latest data")        
        pred, _ = evaluate(
            dataset = (X, y),
            model = model,
            batch_size = int(hyp['batch_size']),
            device = 'cpu'
        )
        
        # post processing
        LOGGER.info(f"Post process prediction result")
        pred = np.array(pred).reshape(-1, len(self.cfg_inference.field['label']))
        pred = pd.DataFrame(pred, columns=self.cfg_inference.field['label'])
        scaler.inverse_transform(
            data = pred,
            columns = self.cfg_inference.field['label'],
            inplace=True
        )
        
        
        tic = datetime.strptime(infer_data['KST_TIME'].max(), "%Y-%m-%d %H:%M:%S")
        toc = tic + timedelta(minutes=self.cfg_preprocessor.pred_len)
        
        LOGGER.info(f"Inference from {tic} to {toc}")
        
        
        pred['KST_TIME'] = gernerate_time_range(tic, toc, interval=1)
        pred['ETL_TIME'] = datetime.strftime(
            datetime.now().replace(minute=0, second=0, microsecond=0), 
            "%Y-%m-%d %H:%M:%S"
        )
            
        # [ INSERT ]
        # insert result to table
        LOGGER.info(f"Insert prediction result to table| Table: {self.cfg_inference.scheme}_{self.cfg_inference.table}")
        Query.dataframe_to_table(
            table_info ={
                'scheme':self.cfg_inference.scheme,
                'table':self.cfg_inference.table
            },
            data = pred,
            conn = self.db_manager.conn,
            table_exists_handling = 'append'
        )
import os

from utils.database import SQLiteDBManager
from utils.logger import setup_logger

LOGGER = setup_logger(__name__, 'train_workflow.log')

class Evaluator:
    
    def __init__(self, cfg_database):
        
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
        
    def run(self):
        
        LOGGER.info("Read test dataset")
        test_data = self.db_manager.fetch_to_dataframe(
            """
            SELECT *
            FROM dw_gld_crypto_transc_candle_upbit_1min_test
            WHERE 1=1
                AND MARKET='KRW-BTC'
            ;    
            """
        )
        
        
        LOGGER.info("Apply sliding window to test data")
        X_test, y_test = split_sliding_widow(
            data = test_data,
            feature_col = self.cfg_preprocessor.feature_cols['gold'],
            input_seq_len = self.cfg_preprocessor.seq_len,
            label_seq_len = 1,
            time_col = 'KST_TIME'
        )
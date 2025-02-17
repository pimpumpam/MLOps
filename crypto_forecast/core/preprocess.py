import os
import sys
from pathlib import Path

from preprocessor.transformation import MultiColumnScaler
from preprocessor.data_preparation import split_train_test
from preprocessor.feature_engineering import aggregate_by_time, amount_of_change_price, amount_of_change_rate
from preprocessor.preprocess import validate_missing_timestamp, validate_missing_values, validate_duplicate_values, fill_time_gaps, fill_missing_values
from utils.logger import setup_logger
from utils.utils import create_seq_values, load_spec_from_config

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]
sys.path.append(str(ROOT))
from db_handler.query import Query
from db_handler.database import SQLiteDBManager


LOGGER = setup_logger(__name__, 'train_workflow.log')

class Preprocessor:
    
    def __init__(self, cfg_meta, cfg_database, cfg_loader, cfg_preprocessor):
        
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_loader = cfg_loader
        self.cfg_preprocessor = cfg_preprocessor
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
    def run(self):
        candle_data = self.db_manager.fetch_to_dataframe(
            """
            SELECT
                MARKET,
                KST_TIME,
                OPEN_PRICE,
                CLOSE_PRICE,
                LOW_PRICE,
                HIGH_PRICE,
                ACC_TRADE_PRICE,
                ACC_TRADE_VOLUME
            FROM dw_brz_crypto_transc_candle_upbit_minutes
            WHERE 1=1
                AND MARKET='KRW-BTC'
            ;
            """
        )
        
        # ***************************** SILVER *****************************
        
        # check missing timestamp
        if not validate_missing_timestamp(candle_data, time_col='KST_TIME'):
            LOGGER.info("Data have at least one missing timestamp or more. Fill missing timestamp")
            candle_data = fill_time_gaps(
                candle_data,
                time_col='KST_TIME',
                start_time=self.cfg_loader.tic, 
                end_time=candle_data['KST_TIME'].max()
            )
            candle_data = fill_missing_values(
                candle_data,
                columns=['MARKET'],
                fill_value='KRW_BTC'
            )
        else:
            LOGGER.info("Data is clean. Any missing timestamp has been detected")
    
        # check missing values
        if not validate_missing_values(candle_data):
            LOGGER.info("Data have at least one missing values or more. Fill missing values")
            candle_data = fill_missing_values(
                candle_data,
                columns=['LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE', 'ACC_TRADE_PRICE', 'ACC_TRADE_VOLUME']
            )            
        else:
            LOGGER.info("Data is clean. Any missing value has been detected.")
        
        # check duplicate values
        if not validate_duplicate_values(candle_data):
            LOGGER.info("Data have at least one duplicated row or more. Remove duplicated row(s)")
            candle_data.drop_duplicates(subset='KST_TIME', inplace=True)
        else:
            LOGGER.info("Data is clean. Any duplicated value has been detected.")
        
        # create derieved feature
        LOGGER.info("Create derieved features")
        candle_data = amount_of_change_price(
            candle_data,
            time_col='KST_TIME',
            feature_cols=self.cfg_preprocessor.feature_cols['bronze'],
            unit='day',
            time_freq=1
        )
        
        candle_data = amount_of_change_rate(
            candle_data,
            time_col='KST_TIME',
            feature_cols=self.cfg_preprocessor.feature_cols['bronze'],
            unit='day',
            time_freq=1
        )
        
        # insert dataframe to table
        LOGGER.info("Insert preprocessed result to database.")
        Query.dataframe_to_table(
            table_info = self.cfg_database.silver['CANDLE_1MIN'],
            data = candle_data,
            conn = self.db_manager.conn,
            exist_handling = 'replace'
        )
 
        
    
        query = Query.drop_dulicate_row(self.cfg_database.silver['CANDLE_1MIN'])
        self.db_manager.execute_query(query)
        
        # ****************************** GOLD ******************************
        
        LOGGER.info("Apply scaler to data")        
        scaler = MultiColumnScaler(self.cfg_preprocessor.transform['SCALER']['name'])
        scaler.fit_transform(
            data=candle_data,
            columns=self.cfg_preprocessor.feature_cols['silver'],
            inplace=True,
            save_pkl=True,
            save_path=self.cfg_preprocessor.transform['SCALER']['save_dir'],
            save_name=self.cfg_preprocessor.transform['SCALER']['save_name']
        )
                
        LOGGER.info("Split data as train and test sets")
        train_1min, test_1min = split_train_test(
            data=candle_data,
            train_ratio=None,
            test_ratio=None,
            time_col = 'KST_TIME',
            split_point=self.cfg_preprocessor.split_point
        )
        
        LOGGER.info("Append scaled dataset to database.")
        Query.dataframe_to_table(
            table_info = self.cfg_database.gold['CANDLE_1MIN'],
            data = train_1min,
            conn = self.db_manager.conn,
            table_name_suffix = 'train',
            table_exists_handling = 'replace' # replace, append
        )
        
        Query.dataframe_to_table(
            table_info = self.cfg_database.gold['CANDLE_1MIN'],
            data = test_1min,
            conn = self.db_manager.conn,
            table_name_suffix = 'test',
            table_exists_handling = 'replace' # replace, append
        )
        
if __name__ == "__main__":
    
    (
        cfg_meta,
        cfg_database,
        cfg_loader, 
        cfg_preprocessor,
        _, # cfg_model
        _, # cfg_hyp
        _, # cfg_train
        _, # cfg_evaluate
    ) = load_spec_from_config('dlinear')
    
    preprocessor = Preprocessor(cfg_meta, cfg_database, cfg_loader, cfg_preprocessor)
    preprocessor.run()
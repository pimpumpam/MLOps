import os
import time
import datetime

from loader.load import inquire_candle_data, inquire_recent_trade_data

from utils.query import Query
from utils.database import SQLiteDBManager
from utils.logger import setup_logger
from utils.utils import create_seq_values, load_spec_from_config


LOGGER = setup_logger(__name__, 'train_workflow.log')

class Loader:
    def __init__(self, cfg_meta, cfg_database, cfg_loader):
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.cfg_loader = cfg_loader
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)

    def run(self):
        LOGGER.info("ETL Crypto Transaction Data from API")    

        for api, prop in self.cfg_database.bronze.items():
            LOGGER.info(f"Inquire \"{self.cfg_loader.platform.upper()} {api}\" Data")

            # inquire data    
            data = []
            for market in self.cfg_loader.market:
                tic = datetime.datetime.strptime(self.cfg_loader.tic, "%Y-%m-%dT%H:%M:%S")
                toc = datetime.datetime.strptime(self.cfg_loader.toc, "%Y-%m-%dT%H:%M:%S")
            
                if api == 'CANDLE':
                    while True:
                        if tic > toc:
                            break

                        datum = inquire_candle_data(
                            market=market,
                            tgt_date=toc,
                            unit = self.cfg_loader.unit,
                            time_unit=self.cfg_loader.time_unit,
                            max_per_attmp=self.cfg_loader.max_per_attmp,
                            params=self.cfg_database.bronze['CANDLE']['params']
                        )
                        data.extend(datum)

                        toc = datetime.datetime.strptime(
                            datum[-1]['candle_date_time_utc'],
                            "%Y-%m-%dT%H:%M:%S"
                        )
                        toc -= datetime.timedelta(seconds=1)

                        time.sleep(0.1)
                
                # elif api == 'TRADE':
                #     while True:    
                #         datum = inquire_recent_trade_data(
                #             market=market,
                #             tgt_date=toc,
                #             max_per_attmp=self.cfg_loader.max_per_attmp,
                #             params = self.cfg_database.bronze['TRADE']['params']
                #         )
                #         if len(datum)==0:
                #             break

                #         data.extend(datum)

                #         toc = datetime.datetime.strptime(
                #              f"{datum[-1]['trade_date_utc']}T{datum[-1]['trade_time_utc']}",
                #              "%Y-%m-%dT%H:%M:%S"
                #         )
                #         toc -= datetime.timedelta(seconds=1)

                #         if toc.day != datetime.datetime.strptime(f"{datum[-1]['trade_date_utc']}", "%Y-%m-%d").day:
                #             break

                #         time.sleep(0.1)

            # create table
            LOGGER.info(f"Create Table as \"{self.cfg_database.bronze[api]['scheme']}_{self.cfg_database.bronze[api]['table']}\"")
            query = Query.create_table(prop)
            self.db_manager.execute_query(query=query)

            # insert data
            LOGGER.info(f"Insert Data into \"{self.cfg_database.bronze[api]['scheme']}_{self.cfg_database.bronze[api]['table']}\"")
            query = Query.insert_data_to_table(prop)
            param_seq = create_seq_values(prop, data)
            self.db_manager.execute_many_query(query, param_seq)


if __name__ == "__main__":
    
    (
        cfg_meta,
        cfg_database,
        cfg_loader, 
        _, # cfg_preprocessor
        _, # cfg_model
        _, # cfg_hyp
        _, # cfg_train
        _, # cfg_evaluate
    ) = load_spec_from_config('dlinear')

    loader = Loader(cfg_meta, cfg_database, cfg_loader)
    loader.run()
import os

from mlflow_manager.utils.utils import create_seq_values
from mlflow_manager.utils.model_tracker import register_model_by_run_id, set_model_stage, tracking_latest_model
from mlflow_manager.utils.experiment_tracker import is_nested, tracking_experiment, tracking_latest_run, tracking_best_run, tracking_best_run_from_parent_run

from sqlite_manager.query import Query
from sqlite_manager.database import SQLiteDBManager


class Deploy:
    
    def __init__(self, cfg_meta, cfg_database):
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
        
    def run(self):
        
        # experiment info
        exp_name = self.cfg_meta.experiment_name
        exp_info = tracking_experiment(experiment_name=exp_name)
        exp_id = exp_info['experiment_id']
        
        # run info
        latest_run_info = tracking_latest_run(experiment_id=exp_id)
        latest_run_id = latest_run_info['run_id']

        # find best run
        if is_nested(latest_run_id):
            best_run = tracking_best_run_from_parent_run(parent_run_id=latest_run_id)
        else:
            best_run = tracking_best_run(run_id=latest_run_id)
    
        # register model
        register_model_info = register_model_by_run_id(
            run_id=best_run['run_id'],
            model_name=self.cfg_meta.register_model_name
        )

        # set model stage
        set_model_stage(
            model_name=register_model_info['name'],
            model_version=register_model_info['version'],
            stage = 'Production'
        )
        
        # latest model info
        model_info = tracking_latest_model(register_model_info['name'])
        
        # create table
        query = Query.create_table(self.cfg_database.register_model)
        self.db_manager.execute_query(query=query)
        
        # insert model info
        query = Query.insert_data_to_table(self.cfg_database.register_model)
        param_seq = create_seq_values(
            table_info=self.cfg_database.register_model,
            data=[model_info],
            column_key='name'
        )
        self.db_manager.execute_many_query(query, param_seq)
        
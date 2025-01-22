import os

from service.utils.model_tracker import register_model_by_run_id, set_model_stage, tracking_latest_model, is_model_registered
from service.utils.experiment_tracker import is_nested, tracking_experiment, tracking_run, tracking_latest_run, tracking_best_run, tracking_best_run_from_parent_run

from db_handler.query import Query
from db_handler.utils import create_seq_values
from db_handler.database import SQLiteDBManager


class Deploy:
    
    def __init__(self, cfg_meta, cfg_database):
        self.cfg_meta = cfg_meta
        self.cfg_database = cfg_database
        self.db_manager = SQLiteDBManager(cfg_database.database_dir)
    
    
    def register_model(self):
        
        UPDATE_DATABASE = False
        
        # 최신 실행 run 중 가장 좋은 성능을 보이는 run 탐색        
        # experiment 탐색
        exp_name = self.cfg_meta.experiment_name
        exp_info = tracking_experiment(experiment_name=exp_name)
        exp_id = exp_info['experiment_id']
        
        # 최근 run 탐색
        latest_run_info = tracking_latest_run(experiment_id=exp_id)
        latest_run_id = latest_run_info['run_id']

        # 최근 run 중 베스트 run 탐색
        if is_nested(latest_run_id):
            best_run = tracking_best_run_from_parent_run(parent_run_id=latest_run_id)
        else:
            best_run = tracking_best_run(run_id=latest_run_id)
            
        
        # 기존에 등록된 모델 있는지 확인
        if is_model_registered(self.cfg_meta.register_model_name):
            # 기존에 등록된 모델 있음
            current_model = tracking_latest_model(
                model_name=self.cfg_meta.register_model_name
            )
            
            current_model_info = tracking_run(
                experiment_id = exp_id,
                run_id = current_model['run_id']
            ).pop()
            
            new_model_info = tracking_run(
                experiment_id = exp_id,
                run_id = best_run['run_id']
            ).pop()
            
            if new_model_info['metrics.RMSE'] < current_model_info['metrics.RMSE']:
                print("New model performance is better. REPLACE model for serving.")
                registered_model_info = register_model_by_run_id(
                    run_id = best_run['run_id'],
                    model_name = self.cfg_meta.register_model_name
                )
                
                set_model_stage(
                    model_name=registered_model_info['name'],
                    model_version=registered_model_info['version'],
                    stage = 'Production'
                )
                
                UPDATE_DATABASE = True
                
            else:
                print("Current model performance is better. MAINTAIN model for serving.")
                
        else:
            # 기존에 등록된 모델 없음
            print("Register New model for serving")
            registered_model_info = register_model_by_run_id(
                run_id = best_run['run_id'],
                model_name = self.cfg_meta.register_model_name
            )
            
            set_model_stage(
                model_name=registered_model_info['name'],
                model_version=registered_model_info['version'],
                stage = 'Production'
            )
            
            UPDATE_DATABASE = True
        
        # 업데이트 된 모델 DB 등록
        if UPDATE_DATABASE:
            # 테이블 생성
            query = Query.create_table(self.cfg_database.register_model)
            self.db_manager.execute_query(query=query)

            # 데이터 insert
            query = Query.insert_data_to_table(self.cfg_database.register_model)
            param_seq = create_seq_values(
                table_info=self.cfg_database.register_model,
                data=[tracking_latest_model(self.cfg_meta.register_model_name)],
                column_key='name'
            )
            self.db_manager.execute_many_query(query, param_seq)
            
            print("Append information of updated serving model to database.")
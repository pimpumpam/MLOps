import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

import mlflow

# from airflow import DAG 
# from airflow.operators.bash import BashOperator
# from airflow.operators.python import PythonOperator
# from airflow.utils.trigger_rule import TriggerRule

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
CONFIG_DIR = os.path.join(ROOT, "configs")
MLFLOW_DIR = os.path.join(ROOT, "mlflow_manager")
PROJECT_DIR = os.path.join(ROOT, "crypto_forecast")
sys.path.append(CONFIG_DIR)
sys.path.append(MLFLOW_DIR)
sys.path.append(PROJECT_DIR)

from run import Run
from compose import CfgMLFlow
from crypto_forecast import CfgMeta

mlflow.set_tracking_uri(CfgMLFlow.server_url)

runner = Run(CfgMeta.config)
# mlflow_manager = # 모델 deploy 관련 프로세스 실행하는 클래스 호출

default_args = {
    'owner': 'Changseon',
    'depends_on_past': False,
    'email': ['kwsxfk8332@gmail.com', 'chicken_cock@naver.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    'CryptoForecast_DLinear',
    default_args=default_args,
    description="Recommendation System using DGL",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 12, 10),
    catchup=False,
    tags=['Toy Project using Crypto Transc Data']
) as dag:
    
    loader = PythonOperator(
        task_id='load_data',
        python_callable=runner.load
    )

    preprocessor = PythonOperator(
        task_id='preprocessing_data',
        python_callable=runner.preprocess
    )

    trainer = PythonOperator(
        task_id='train_model',
        python_callable=runner.train,
        provide_context=True
    )

    evaluator = PythonOperator(
        task_id='evaluate_model',
        python_callable=runner.evaluate,
        provide_context=True
    )

    loader >> preprocessor >> trainer >> evaluator
    
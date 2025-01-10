import os
import sys
import pendulum
from pathlib import Path
from datetime import datetime, timedelta

import mlflow

from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
sys.path.append(str(ROOT))

from crypto_forecast.run import Run
from compose.services import CfgMLFlow
from compose.crypto_forecast import CfgMeta, CfgDatabase
from mlflow_manager.deploy import Deploy

mlflow.set_tracking_uri(CfgMLFlow.server_url)

runner = Run(CfgMeta.config)
deployer = Deploy(CfgMeta, CfgDatabase)


default_args = {
    'owner': 'Changsun',
    'depends_on_past': False,
    'email': ['kwsxfk8332@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    'CryptoForecast_RNN',
    default_args=default_args,
    description="MLOps Project Using Crypto Data",
    start_date=pendulum.datetime(2025, 1, 8, tz="Asia/Seoul"),
    schedule=timedelta(hours=1),
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
        python_callable=runner.train
    )

    evaluator = PythonOperator(
        task_id='evaluate_model',
        python_callable=runner.evaluate
    )

    loader >> preprocessor >> trainer >> evaluator
    
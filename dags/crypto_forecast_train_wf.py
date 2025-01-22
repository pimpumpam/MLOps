import os
import sys
import pendulum
from pathlib import Path
from datetime import timedelta

import mlflow

from airflow import DAG 
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
sys.path.append(str(ROOT))

from service.deploy import Deploy
from crypto_forecast.run import Run
from compose.services import CfgMLFlow, CfgSlack
from compose.crypto_forecast import CfgMeta, CfgDatabase
from messenger.message import AirflowMessenger

mlflow.set_tracking_uri(CfgMLFlow.server_url)

# objects
runner = Run(CfgMeta.config)
messenger = AirflowMessenger(CfgSlack)
deployer = Deploy(CfgMeta, CfgDatabase)

# globals
DAG_NAME = "CryptoForecast_Train_WorkFlow"
DEFAULT_ARGS = {
    'owner': 'Changsun',
    'depends_on_past': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'on_failure_callback': messenger.send_failure_task_info_message
}

# dags
with DAG(
    DAG_NAME,
    default_args=DEFAULT_ARGS,
    description="Train Crypto Forecast Model",
    start_date=pendulum.datetime(2025, 1, 8, tz="Asia/Seoul"),
    schedule=None,
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
    
    deployor = PythonOperator(
        task_id='deploy_model',
        python_callable=deployer.register_model
    )
    
    messenger = PythonOperator(
        task_id='slack_messenger',
        python_callable=messenger.send_whole_task_info_message,
        op_args=[DAG_NAME]
    )

    loader >> preprocessor >> trainer >> evaluator >> deployor >> messenger
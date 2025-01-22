import os
import sys
import pendulum
from pathlib import Path
from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
sys.path.append(str(ROOT))

from crypto_forecast.run import Run
from compose.services import CfgSlack
from compose.crypto_forecast import CfgMeta
from messenger.message import AirflowMessenger


# objects
runner = Run(CfgMeta.config)
messenger = AirflowMessenger(CfgSlack)

# globals
DAG_NAME = "CryptoForecast_Inference_WorkFlow"
DEFAULT_ARGS = {
    'owner': 'Changsun',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'on_failure_callback': messenger.send_failure_task_info_message
}

# dags
with DAG(
    DAG_NAME,
    default_args=DEFAULT_ARGS,
    description="Request Crypto Transc Data",
    start_date=pendulum.datetime(2025, 1, 8, tz="Asia/Seoul"),
#     schedule=timedelta(days=1),
    schedule_interval='3 * * * *', # 분(0~59) 시(0~23) 일(1~31) 월(1~12) 요일(0~6, 0:일요일)
    catchup=False,
    tags=['Toy Project using Crypto Transc Data']
) as dag:
    
    inferer = PythonOperator(
        task_id='inference_data',
        python_callable = runner.inference
    )
    
    messenger = PythonOperator(
        task_id='slack_messenger',
        python_callable=messenger.send_whole_task_info_message,
        op_args=[DAG_NAME]
    )
    
    
    inferer >> messenger
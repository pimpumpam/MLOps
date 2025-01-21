import os
import sys
import pendulum
from pathlib import Path
from datetime import timedelta

import mlflow

from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
sys.path.append(str(ROOT))

from service.deploy import Deploy
from crypto_forecast.run import Run
from compose.services import CfgMLFlow, CfgSlack
from compose.crypto_forecast import CfgMeta, CfgDatabase
from messenger.message import AirflowMessenger


# objects
mlflow.set_tracking_uri(CfgMLFlow.server_url)
runner = Run(CfgMeta.config)
messenger = AirflowMessenger(CfgSlack)

# globals
DAG_NAME = "CryptoForecast_Monitoring_WorkFlow"
DEFAULT_ARGS = {
    'owner': 'Changsun',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'on_failure_callback': messenger.send_failure_task_info_message
}


# def task_that_fails():
#     raise ValueError("This task is set to fail!")

def branch_task(ti):
    status = ti.xcom_pull(task_ids='monitor')
    
    if status == 'update':
        return 'train_workflow'
    
    else:
        return 'complete_msg'


with DAG(
    DAG_NAME,
    default_args=DEFAULT_ARGS,
    description="Monitoring Crypto Forecast Model",
    start_date=pendulum.datetime(2025, 1, 8, tz="Asia/Seoul"),
    schedule_interval='5 * * * * ',
    catchup=False,
    tags=['Toy Project using Crypto Transc Data']
) as dag:
    
    
#     tester = PythonOperator(
#         task_id = 'tester',
#         python_callable = task_that_fails
#     )
    
    monitor = PythonOperator(
        task_id = 'monitor',
        python_callable = runner.monitoring
    )
    
    branch = BranchPythonOperator(
        task_id = 'branch_update_model',
        python_callable = branch_task,
        provide_context=True
    )
    
    train_workflow = TriggerDagRunOperator(
        task_id = 'train_workflow',
        trigger_dag_id='CryptoForecast_Train_WorkFlow',
        wait_for_completion=True
    )
    
    complete = BashOperator(
        task_id = 'complete_msg',
        bash_command = 'echo "Maintain Current Model"'
    )
    
    monitor >> branch >> [train_workflow, complete]
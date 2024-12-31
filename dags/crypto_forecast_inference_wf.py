import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]
PROJECT_DIR = os.path.join(ROOT, "crypto_forecast")
sys.path.append(PROJECT_DIR)




default_args = {
    'owner': 'Changseon',
    'depends_on_past': False,
    'email': ['kwsxfk8332@gmail.com', 'chicken_cock@naver.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}
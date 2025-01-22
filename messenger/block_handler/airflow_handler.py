from datetime import datetime

from airflow.settings import Session
from airflow.models import DagRun, TaskInstance

from slack_sdk.models.blocks import SectionBlock
from slack_sdk.models.blocks.basic_components import MarkdownTextObject

from compose.services import CfgAirFlow


AIRFLOW_SERVER_URL = CfgAirFlow.server_url

def get_header_block(header_text):
    """
    Header 블록 생성
    
    parameter
    ----------
    header_text(str):
    
    return
    ----------
    (slack_sdk.SectionBlock):
    
    """
    return SectionBlock(text=MarkdownTextObject(text=header_text))


def get_dags_block(dag_name):
    """
    DAG에 대한 정보 조회 및 블록 생성
    
    parameter
    ----------
    dag_name(str):
    
    return
    ----------
    (slack_sdk.SectionBlock):
    
    """
    session = Session()
    
    dags = (
        session.query(DagRun)
        .filter(DagRun.dag_id==dag_name)
        .order_by(DagRun.execution_date.desc())
        .first()
    )
    
    section = "*⚙️ DAGs Information* ⚙️ \n"
    section += (
        f"\t- Name: {dags.dag_id} \n"
        f"\t- State: {dags.state.upper() if dags.state=='failed' else dags.state} \n"
        f"\t- Start Time: {datetime.strftime(dags.start_date, '%Y-%m-%d %H:%M:%S')} \n"
    )
    
    session.close()
    
    return SectionBlock(text=MarkdownTextObject(text=section.strip()))


def get_tasks_info(dag_name):
    """
    DAG 내 task에 대한 정보 조회 및 블록 생성
    
    parameter
    ----------
    dag_name(str):
    
    return
    ----------
    task_infos(list):
    
    """
    session = Session()
    
    dags = (
        session.query(DagRun)
        .filter(DagRun.dag_id==dag_name)
        .order_by(DagRun.execution_date.desc())
        .first()
    )
    
    tasks = (
        session.query(TaskInstance)
        .filter(TaskInstance.dag_id==dag_name, TaskInstance.run_id==dags.run_id)
        .all()
    )
    
    task_infos = []
    for task in tasks:
        task_info = {}
        
        task_info['name'] = task.task_id
        task_info['state'] = task.state.upper() if task.state=='failed' else task.state
        task_info['execution_time'] = datetime.strftime(task.start_date, '%Y-%m-%d %H:%M:%S')
        task_info['duration'] = round(task.duration, 2) if task.duration is not None else 0
        task_info['log_info'] = f"{AIRFLOW_SERVER_URL}/log?{task.log_url.split('log?')[-1]}"
        
        task_infos.append(task_info)
        
    session.close()
        
    return task_infos


def get_task_block(task):
    
    """
    단일 Task 정보에 대한 slcak block 텍스트 생성
    
    parameter
    ----------
    task(dict): 인스턴스(key)와 해당 값(value)으로 이루어진 딕셔너리. {인스턴스1: 값1, 인스턴스2: 값2, ...}
    
    return
    ----------
    
    """
    
    section = "*🗂️ Task Information 🗂️* \n"
    
    for key, val in task.items():
        section += f"\t- {key}: {val} \n"
    
    
    return SectionBlock(text=MarkdownTextObject(text=section.strip()))
    
    
def get_tasks_block(tasks):
    """
    다수의 Task 정보에 대한 slack block 텍스트 생성
    
    parameter
    ----------
    tasks(list): Task에 대한 정보들이 dictionary로 구성 된 list
    
    return
    ----------
    (list)
    
    """
    
    section = [
        SectionBlock(
            text=MarkdownTextObject(text="*🗂️ Tasks Information 🗂️*")
        )
    ]
    
    fields = []
    
    for idx, task in enumerate(tasks):
        
        if task['state']=='running':
            continue
        
        block = (
            f"*Task No.{idx+1}* \n"
            f"\t - Name: {task['name']} \n"
            f"\t - State: {task['state']} \n"
            f"\t - Execution Time: {task['execution_time']} \n"
            f"\t - Duration: {task['duration']}s \n"
            f"\t - Log History: <{task['log_info']}|View Logs> \n"
        )
        
        fields.append(MarkdownTextObject(text=block))
        
    for i in range(0, len(fields), 2):
        section.append(SectionBlock(fields=fields[i:i+2]))
        
    return section
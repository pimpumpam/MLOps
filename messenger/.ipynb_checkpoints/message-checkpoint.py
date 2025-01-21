from datetime import datetime
from slack_sdk.webhook import WebhookClient
from slack_sdk.models.blocks import DividerBlock

from messenger.block_handler.airflow_handler import get_header_block, get_task_block, get_tasks_info, get_tasks_block, get_dags_block
from compose.services import CfgSlack


class AirflowMessenger:
    
    def __init__(self, cfg_slack):
        self.cfg_slack = cfg_slack
        self.webhook = WebhookClient(cfg_slack.slack_webhook_url)
        
    def send_failure_task_info_message(self, context):
        
        # header
        header_block = get_header_block(
            header_text = "*🚨 Alert 🚨*\nTask Failure Details During Workflow Execution Scheduled in *Airflow*"
        )
        
        # task info
        task_dict = {
            "DAG Name": context.get('dag').dag_id,
            "Task Name": context.get('task_instance').task_id,
            "State": context.get('task_instance').state.upper(),
            "Execution Time": datetime.strftime(context.get('task_instance').execution_date, '%Y-%m-%d %H:%M:%S'),
            "Attempt Time": context.get('task_instance').try_number
        }
        task_block = get_task_block(task_dict)
        
        # message block
        blocks = [
            header_block,
            DividerBlock(),
            task_block
        ]
        
        # send message
        response = self.webhook.send(
            text="Airflow Task Failure Information Message",
            blocks=[block.to_dict() for block in blocks]
        )
        
        print(f"Status Code: {response.status_code} | Body: {response.body}")
        
    
    def send_whole_task_info_message(self, dag_name):
        
        # header
        header_block = get_header_block(
            header_text = "*📢 Notification 📢*\nThis is the Execution Result History of the Workflows Scheduled in *Airflow*"
        )
        
        # dags info
        dag_block = get_dags_block(
            dag_name=dag_name
        )
        
        # tasks info
        task_block = get_tasks_block(
            tasks=get_tasks_info(
                dag_name=dag_name
            )
        )
        
        # message blocks
        blocks = [
            header_block,
            DividerBlock(),
            dag_block
        ]
        blocks.extend(task_block)
        
        # send message
        response = self.webhook.send(
            text="Airflow DAGs Information Message",
            blocks=[block.to_dict() for block in blocks]
        )
        
        print(f"Status Code: {response.status_code} | Body: {response.body}")
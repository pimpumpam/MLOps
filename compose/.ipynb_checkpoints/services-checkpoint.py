class CfgMLFlow:
    server_url = "http://192.168.150.103:8334"

class CfgAirFlow:
    server_url = "http://192.168.150.103:8337"
    dags_dir = "/data1/MLOps/Airflow/MLOps/dags"
    
class CfgSlack:
    slack_webhook_url = "https://hooks.slack.com/services/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"
    # mlflow_webhook_url = "" # slack api 내 webhook 생성 부분에서 채널 웹훅 생성 시 발급 되는 url 주소 복붙
    # airflow_webhook_url = "" # slack api 내 webhook 생성 부분에서 채널 웹훅 생성 시 발급 되는 url 주소 복붙
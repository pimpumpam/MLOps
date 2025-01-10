class CfgMLFlow:
    server_url = "http://127.0.0.1:8334"

class CfgAirFlow:
    server_url = "http://127.0.0.1:8332"
    dags_dir = "/Users/pimpumpam/my_Python/MLOps/dags"
    
class CfgSlack:
    mlflow_webhook_url = "" # slack api 내 webhook 생성 부분에서 채널 웹훅 생성 시 발급 되는 url 주소 복붙
    airflow_webhook_url = "" # slack api 내 webhook 생성 부분에서 채널 웹훅 생성 시 발급 되는 url 주소 복붙
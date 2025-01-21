import traceback

import mlflow
from mlflow.tracking import MlflowClient

from service.utils.utils import timestamp_to_datetime

ALIAS = ["Archived", "Staging", "Production"]


def register_model_by_run_id(run_id=None, **kwargs):
    assert run_id, f"Argument \"run_id\" is required"
    
    model_uri = f'runs:/{run_id}/model'
    
    if 'model_name' in kwargs:
        model_name = kwargs['model_name']
    else:
        model_name = mlflow.get_run(run_id).info.run_name    
    
    registered_model = mlflow.register_model(
        model_uri=model_uri,
        name=model_name
    )
    
    return dict(registered_model)


def set_model_stage(model_name, model_version, stage):
    
    assert stage in ALIAS, f"Argument \'stage\' must be one of {ALIAS}"
    
    try:
        client = MlflowClient()
                
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=stage,
            archive_existing_versions=True
        )
        print(f"Success Convert model stage.\n\tModel: \'{model_name}\' | Version: \'{model_version}\' | Stage: \'{stage}\'")
    
    except Exception:
        err_msg = traceback.format_exc()
        print(err_msg)
        

def tracking_registered_model(model_name):
    try:
        client = MlflowClient()
        
        return dict(client.get_registered_model(name=model_name))
        
    except Exception:
        err_msg = traceback.format_exc()
        print(err_msg)
        

def tracking_latest_model(model_name):
    
    model_info = tracking_registered_model(model_name)
    latest_version_info = dict(model_info['latest_versions'][-1])
    
    model_info_dict = {
        'NAME': model_info['name'],
        'VERSION': latest_version_info['version'],
        'CREATION_TIME': timestamp_to_datetime(model_info['creation_timestamp']/1000),
        'LATEST_UPDATE_TIME': timestamp_to_datetime(latest_version_info['last_updated_timestamp']/1000),
        'RUN_ID': latest_version_info['run_id'],
        'STAGE': latest_version_info['current_stage'],
        'SOURCE': latest_version_info['source']
    }
    
    return model_info_dict


def is_model_registered(model_name):
    client = MlflowClient()
    
    for model in client.search_registered_models():
        if model.name == model_name:
            return True
            
        else:
            return False
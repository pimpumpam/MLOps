import traceback

import mlflow
from mlflow.tracking import MlflowClient

ALIAS = ["Archived", "Staging", "Production"]


def register_model_by_run_id(run_id=None):
    assert run_id, f"Argument \"run_id\" is required"
    
    model_uri = f'runs:/{run_id}/model'
    
    run_name = mlflow.get_run(run_id).info.run_name    
    
    registered_model = mlflow.register_model(
        model_uri=model_uri,
        name=run_name
    )
    
    return dict(registered_model)


def set_model_stage(model_name, model_version, stage):
    
    assert stage in ALIAS, f"Argument \'stage\' must be one of {ALIAS}"
    
    try:
        client = MlflowClient()
        
        current_model_info = dict(
            client.get_model_version(
                name=model_name, 
                version=model_version
            )
        )
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=stage
        )
        print(f"Success Convert model stage.\n\tModel: \'{model_name}\' | Version: \'{model_version}\' | Stage: \'{current_model_info['current_stage']}\' -> \'{stage}\'")
    
    except Exception:
        err_msg = traceback.format_exc()
        print(err_msg)
        
    
    
import mlflow


def is_nested(run_id):
    run_info = mlflow.get_run(run_id)
    experiment_id = run_info.info.experiment_id
    
    child_run = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.mlflow.parentRunId = '{run_id}'"
    )
        
    return True if len(child_run)>0 else False


def tracking_experiment(experiment_name=None, experiment_id=None):
    
    assert experiment_id or experiment_name, f"At least one argument \"experiment_id\" or \"experiment_name\" is required"

    if experiment_id:
        if not isinstance(experiment_id, str):
            experiment_id = str(experiment_id)
            
        return dict(mlflow.get_experiment(experiment_id))
        
    elif experiment_name:
        
        return dict(mlflow.get_experiment_by_name(experiment_name))
            
    
def tracking_run(experiment_id, run_id=None, run_name=None):
    assert run_id or run_name, f"At least one argument \"run_id\" or \"run_name\" is required"
    
    if run_id:
        if not isinstance(run_id, str):
            run_id = str(run_id)
        
        return mlflow.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"run_id='{run_id}'"
        ).to_dict('records')
        
    elif run_name:
        return mlflow.search_runs(
            experiment_ids=[experiment_id],
            filter_string=f"tags.mlflow.runName='{run_name}'"
        ).to_dict('records')
        
        
def tracking_latest_run(experiment_id=None, run_id=None):
    
    assert experiment_id or run_id, f"At least one argument \"experiment_id\" or \"run_id\" is required"
    
    if not experiment_id:
        run_info = mlflow.get_run(run_id)
        experiment_id = run_info.info.experiment_id
    
    all_runs = mlflow.search_runs(
        experiment_ids = [experiment_id],
        order_by=['attributes.created DESC']
    )
        
    try:
        return all_runs[all_runs['tags.mlflow.parentRunId'].isna()].iloc[0].to_dict()
    except:
        return all_runs.iloc[0].to_dict()
    
    
def tracking_best_run(experiment_id=None, run_id=None, metric='RMSE'):
    
    assert experiment_id or run_id, f"At least one argument \"experiment_id\" or \"run_id\" is required"
    
    if not experiment_id:
        run_info = mlflow.get_run(run_id)
        experiment_id = run_info.info.experiment_id
        
    all_runs = mlflow.search_runs(
        experiment_ids = [experiment_id],
        order_by=[f"metrics.{metric} ASC"]
    )
    
    return all_runs.iloc[0].to_dict()


def tracking_best_run_from_parent_run(experiment_id=None, parent_run_id=None, metric='RMSE'):
    
    assert parent_run_id, f"Argument \"parent_run_id\" is required"
        
    if not experiment_id:
        run_info = mlflow.get_run(parent_run_id)
        experiment_id = run_info.info.experiment_id
        
    nested_runs = mlflow.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"tags.mlflow.parentRunId = '{parent_run_id}'",
        order_by=[f'metrics.{metric} ASC']
    )
    
    return nested_runs.iloc[0].to_dict()
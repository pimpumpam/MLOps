class CfgMeta:
    experiment_name = "crypto_forecast"
    experiment_dir = '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/crypto_forecast'
    config = 'dlinear'
    register_model_name = 'CryptoForcast_GRU'
    
    
class CfgDatabase:
    engine = 'Sqlite3'
    database_dir = '/Users/pimpumpam/my_Python/MLOps/crypto_forecast/crypto.db'
    register_model = {
        'scheme': 'dw_model',
        'table': 'registred_model',
        'columns': [
            {'name': 'MODEL_NAME', 'type': 'STRING'},
            {'name': 'VERSION', 'type': 'STRING'},
            {'name': 'CREATION_TIME', 'type': 'STRING'},
            {'name': 'LATEST_UPDATE_TIME', 'type': 'INTEGER'},
            {'name': 'RUN_ID', 'type': 'INTEGER'},
            {'name': 'STAGE', 'type': 'INTEGER'},
            {'name': 'SOURCE', 'type': 'INTEGER'}
        ]
    }
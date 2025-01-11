class CfgMeta:
    name = 'CRYPTO_FORECAST'
    exp_name = 'crypto_forecast'
    mlflow = {
        'DASHBOARD_URL': 'http://127.0.0.1:8334',
        'DATABASE_DIR': '/Users/pimpumpam/my_Python/MLOps/mlflow.db',
        'ARTIFACT_DIR': '/Users/pimpumpam/my_Python/MLOps/artifacts'
    }
    
class CfgDatabase:
    engine = 'Sqlite3'
    database_dir = '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/crypto_forecast/crypto.db'
    bronze = {
        'CANDLE' : {
            'params': {},
            'scheme': 'dw_brz',
            'table' : 'crypto_transc_candle_upbit_minutes',
            'columns': [
                {'source': 'market', 'name': 'MARKET', 'type': 'STRING'},
                {'source': 'candle_date_time_utc', 'name': 'UTC_TIME', 'type': 'STRING'},
                {'source': 'candle_date_time_kst', 'name': 'KST_TIME', 'type': 'STRING'},
                {'source': 'opening_price', 'name': 'OPEN_PRICE', 'type': 'INTEGER'},
                {'source': 'trade_price', 'name': 'CLOSE_PRICE', 'type': 'INTEGER'},
                {'source': 'low_price', 'name': 'LOW_PRICE', 'type': 'INTEGER'},
                {'source': 'high_price', 'name': 'HIGH_PRICE', 'type': 'INTEGER'},
                {'source': 'candle_acc_trade_price', 'name': 'ACC_TRADE_PRICE', 'type': 'REAL'},
                {'source': 'candle_acc_trade_volume', 'name': 'ACC_TRADE_VOLUME', 'type': 'REAL'}
            ]
        },
        'TRADE' : {
            'params' : {'cursor' : None, 'days_ago' : 1},
            'scheme': 'dw_brz',
            'table' : 'crypto_transc_recent_trade_upbit',
            'columns' : [
                {'source': 'market', 'name': 'MARKET', 'type': 'STRING'},
                {'source': 'trade_date_utc', 'name': 'UTC_DATE', 'type': 'STRING'},
                {'source': 'trade_time_utc', 'name': 'UTC_TIME', 'type': 'STRING'},
                {'source': 'timestamp', 'name': 'TIMESTAMP', 'type': 'STRING'},
                {'source': 'trade_price', 'name': 'CLOSE_PRICE', 'type': 'INTEGER'},
                {'source': 'trade_volume', 'name': 'CLOSE_VOLUME', 'type': 'REAL'},
                {'source': 'prev_closing_price', 'name': 'PREV_CLOSE_PRICE', 'type': 'INTEGER'},
                {'source': 'change_price', 'name': 'CHANGE_PRICE', 'type': 'INTEGER'},
                {'source': 'ask_bid', 'name': 'ASK_BID', 'type': 'STRING'},
                {'source': 'sequential_id', 'name': 'SEQUENTIAL_ID', 'type': 'STRING'}
            ]
        }
    }
    silver = {
        'CANDLE_1MIN': {
            'scheme': 'dw_slv',
            'table': 'crypto_transc_candle_upbit_1min',
            'columns': [
                {'name': 'MARKET', 'type': 'STRING'},
                {'name': 'KST_TIME', 'type': 'STRING'},
                {'name': 'OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'DIFF_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'DIFF_ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'RATIO_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'RATIO_ACC_TRADE_VOLUME', 'type': 'REAL'}
            ]
        },
        
        'CANDLE_5MIN': {
            'scheme': 'dw_slv',
            'table': 'crypto_transc_candle_upbit_5min',
            'columns': [
                {'name': 'MARKET', 'type': 'STRING'},
                {'name': 'KST_TIME', 'type': 'STRING'},
                {'name': 'OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'DIFF_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'DIFF_ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'RATIO_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'RATIO_ACC_TRADE_VOLUME', 'type': 'REAL'}
            ]
        }
    }
    gold = {
        'CANDLE_1MIN': {
            'scheme': 'dw_gld',
            'table': 'crypto_transc_candle_upbit_1min',
            'columns': [
                {'name': 'MARKET', 'type': 'STRING'},
                {'name': 'KST_TIME', 'type': 'STRING'},
                {'name': 'OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'DIFF_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'DIFF_ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'RATIO_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'RATIO_ACC_TRADE_VOLUME', 'type': 'REAL'}
            ]
        },
        
        'CANDLE_5MIN': {
            'scheme': 'dw_gld',
            'table': 'crypto_transc_candle_upbit_5min',
            'columns': [
                {'name': 'MARKET', 'type': 'STRING'},
                {'name': 'KST_TIME', 'type': 'STRING'},
                {'name': 'OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'DIFF_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'DIFF_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'DIFF_ACC_TRADE_VOLUME', 'type': 'REAL'},
                {'name': 'RATIO_OPEN_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_CLOSE_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_LOW_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_HIGH_PRICE', 'type': 'INTEGER'},
                {'name': 'RATIO_ACC_TRADE_PRICE', 'type': 'REAL'},
                {'name': 'RATIO_ACC_TRADE_VOLUME', 'type': 'REAL'}
            ]
        }
    }


class CfgLoader:
    platform = 'upbit'
    market = ['KRW-BTC', 'BTC-ETH', 'BTC-XRP'] # 비트코인, 이더리움, 리플
    unit = 'minutes' # minutes, days, weeks, months
    time_unit = 1 # 분 봉의 단위
    tic = '2024-11-01T00:00:00'
    toc = '2024-12-31T23:59:00'
    max_per_attmp = 180 # 한번에 가져 올 데이터 개수 (최대 200)


class CfgPreprocessor:
    platform = 'upbit'
    unit = 'minutes' # minutes, days, weeks, months
    seq_len = 60 # 1시간
    split_ratio = 0.7
    split_point = '2024-12-25T23:59:59'
    transform = {
        'SCALER': {
            'name': 'MinMaxScaler',
            'save_dir' : '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/crypto_forecast/static',
            'save_name': 'candle_scaler'
        },
        'ENCODER': {
            'name': 'sklearn.preprocessing.LabelEncoder',
            'save_dir' : '/Users/pimpumpam/my_Python/MLOps/crypto_forecast/static',
            'save_name': 'candle_encoder'
        }
    }    
    feature_cols = {
        'bronze': [
            'LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE',
            'ACC_TRADE_PRICE', 'ACC_TRADE_VOLUME'
        ],
        'silver': [
            'LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE',
            'ACC_TRADE_PRICE', 'ACC_TRADE_VOLUME',
            'DIFF_LOW_PRICE', 'DIFF_HIGH_PRICE', 'DIFF_OPEN_PRICE', 'DIFF_CLOSE_PRICE', 'DIFF_ACC_TRADE_PRICE', 'DIFF_ACC_TRADE_VOLUME',
            'RATIO_LOW_PRICE', 'RATIO_HIGH_PRICE', 'RATIO_OPEN_PRICE', 'RATIO_CLOSE_PRICE', 'RATIO_ACC_TRADE_PRICE', 'RATIO_ACC_TRADE_VOLUME'
        ],
        'gold': [
            'LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE',
            'ACC_TRADE_PRICE', 'ACC_TRADE_VOLUME',
            'DIFF_LOW_PRICE', 'DIFF_HIGH_PRICE', 'DIFF_OPEN_PRICE', 'DIFF_CLOSE_PRICE', 'DIFF_ACC_TRADE_PRICE', 'DIFF_ACC_TRADE_VOLUME',
            'RATIO_LOW_PRICE', 'RATIO_HIGH_PRICE', 'RATIO_OPEN_PRICE', 'RATIO_CLOSE_PRICE', 'RATIO_ACC_TRADE_PRICE', 'RATIO_ACC_TRADE_VOLUME'
        ]
    }

class CfgModel:
    platform = 'upbit'
    unit = 'minutes' # minutes, days, weeks, months
    name = 'GRU'
    lstm_layer = {
        'num_layers': 2,
        'hidden_dim': 50,
        'architecture': [
            ['nn.LSTM', [18, 50, 2, True, True]],
        ]
    }
    gru_layer = {
        'num_layers': 2,
        'hidden_dim': 50,
        'architecture': [
            ['nn.GRU', [18, 50, 2, True, True]],
        ]
    }
    linear_layer = {
        'num_layers': 2,
        'architecture': [
            ['nn.Linear', [3000, 4]], # GRU_Hidden x num_seq
        ]
    }


class CfgHyperParameter:
    num_epoch = [1]
    learning_rate = [0.01]
    batch_size = [20]
    

class CfgTrain:
    scheme = 'dw_gld'
    table = 'crypto_transc_candle_upbit_1min_train'
    field = {
        'feature': [
            'LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE',
            'ACC_TRADE_PRICE', 'ACC_TRADE_VOLUME',
            'DIFF_LOW_PRICE', 'DIFF_HIGH_PRICE', 'DIFF_OPEN_PRICE', 'DIFF_CLOSE_PRICE', 'DIFF_ACC_TRADE_PRICE', 'DIFF_ACC_TRADE_VOLUME',
            'RATIO_LOW_PRICE', 'RATIO_HIGH_PRICE', 'RATIO_OPEN_PRICE', 'RATIO_CLOSE_PRICE', 'RATIO_ACC_TRADE_PRICE', 'RATIO_ACC_TRADE_VOLUME'
        ],
        'label': ['LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE']
    }

class CfgEvaluate:
    scheme = 'dw_gld'
    table = 'crypto_transc_candle_upbit_1min_test'
    field = {
        'feature': [
            'LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE',
            'ACC_TRADE_PRICE', 'ACC_TRADE_VOLUME',
            'DIFF_LOW_PRICE', 'DIFF_HIGH_PRICE', 'DIFF_OPEN_PRICE', 'DIFF_CLOSE_PRICE', 'DIFF_ACC_TRADE_PRICE', 'DIFF_ACC_TRADE_VOLUME',
            'RATIO_LOW_PRICE', 'RATIO_HIGH_PRICE', 'RATIO_OPEN_PRICE', 'RATIO_CLOSE_PRICE', 'RATIO_ACC_TRADE_PRICE', 'RATIO_ACC_TRADE_VOLUME'
        ],
        'label': ['LOW_PRICE', 'HIGH_PRICE', 'OPEN_PRICE', 'CLOSE_PRICE']
    }
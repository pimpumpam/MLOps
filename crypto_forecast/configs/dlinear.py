class CfgMeta:
    name = 'CRYPTO_FORECAST'
    exp_name = 'crypto_forecast'
    database = {
        'ENGINE': 'Sqlite3',
        'DATABASE_DIR' : '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/crypto_forecast/crypto.db',
    }
    mlflow = {
        'DASHBOARD_URL': 'http://127.0.0.1:8331',
        'DATABASE_DIR': '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/mlflow.db',
        'ARTIFACT_DIR': '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/artifacts'
    }


class CfgLoader:
    platform = 'upbit'
    market = ['KRW-BTC', 'BTC-ETH', 'BTC-XRP'] # 비트코인, 이더리움, 리플
    unit = 'minutes' # minutes, days, weeks, months
    time_unit = 1 # 분 봉의 단위
    tic = '2024-11-01T00:00:00'
    toc = '2024-12-31T23:59:00'
    max_per_attmp = 180 # 한번에 가져 올 데이터 개수 (최대 200)
    quotation = {
        'CANDLE' : {
            'params': {},
            'scheme': 'dw_brz',
            'table' : f'crypto_transc_candle_{platform}_{unit}',
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
            'table' : f'crypto_transc_recent_trade_{platform}',
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


class CfgPreprocessor:
    platform = 'upbit'
    unit = 'minutes' # minutes, days, weeks, months
    seq_len = 120
    transform = {
        'SCALER': {
            'name': 'sklearn.preprocessing.MinMaxScaler',
            'save_dir' : '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/crypto_forecast/static'
        },
        'ENCODING': {
            'name': 'sklearn.preprocessing.LabelEncoder',
            'save_dir' : '/Users/pimpumpam/Desktop/myScript/MLOps_Prj/mlOps_prj/crypto_forecast/static'
        }
    }    
    

class CfgModel:
    platform = 'upbit'
    unit = 'minutes' # minutes, days, weeks, months
    name = 'DLinear'
    


class CfgHyperParameter:
    num_epoch = 300
    learning_rate = 0.005
    

class CfgEvaluate:
    platform = 'upbit'
    unit = 'minutes' # minutes, days, weeks, months
    table = f'crypto_transaction_{platform}_{unit}'
   
import datetime
import requests

from utils.logger import setup_logger

LOGGER = setup_logger(__name__, 'train_workflow.log')
    
def inquire_candle_data(market, tgt_date, unit, time_unit=1, max_per_attmp=180, **kwargs):
    """
    특정 시점의 거래소 캔들 API 데이터 조회
    참고: https://docs.upbit.com/reference/%EB%B6%84minute-%EC%BA%94%EB%93%A4-1

    parameter
    ----------
    market(str): 종목 명
    tgt_date(str): 조회 대상 날짜
    unit(str): 시간 단위. "minutes", "days", "weeks", "months" 중 선택 가능.
    time_unit(int): unit 인자에 대한 수치 값. unit='minutes'이고 time_unit=1이면 1분 단위 데이터 조회.
    max_per_attmp(int): 한 번의 request에 가져 올 데이터 수

    return
    ----------
    (json): API 기반 데이터 조회 결과

    """
    if not isinstance(tgt_date, str):
        tgt_date = datetime.datetime.strftime(tgt_date, "%Y-%m-%dT%H:%M:%S")

    URL = f"https://api.upbit.com/v1/candles/{unit}/{time_unit}"
    PARAMS = {
        "market" : market,
        "to" : tgt_date,
        "count" : max_per_attmp
    }

    for k, v in kwargs['params'].items():
        if v:
            PARAMS[k] = v

    try:
        response = requests.get(URL, params=PARAMS)
        response.raise_for_status()
        
        return response.json()

    except requests.exceptions.RequestException as e:  
        LOGGER.error(f"Error Fetching Data from UpBit : {e}")
        
        return None
    

def inquire_recent_trade_data(market, tgt_date, max_per_attmp=180, **kwargs):
    """
    특정 시간 기준 최근 거래 내역 조회
    참고: https://docs.upbit.com/reference/%EC%B5%9C%EA%B7%BC-%EC%B2%B4%EA%B2%B0-%EB%82%B4%EC%97%AD

    parameter
    ----------
    market(str): 종목 명
    tgt_time(str): 마지막 체결 시각. "HHmmss" 또는 "HH:mm:ss" 형식.
    cursor(str): 페이지 네이션 커서 (sequential_id). ref: Upbit API Reference
    days_ago(int): 최근 체결 날짜 기준 이전 시점 범위. 1~7일 중 선택 가능. ref: Upbit API Reference
    max_per_attmp(int): 한 번의 request에 가져 올 데이터 수

    return
    ----------
    (json): API 기반 데이터 조회 결과

    """
    if not isinstance(tgt_date, str):
        tgt_date = datetime.datetime.strftime(tgt_date, "%Y-%m-%dT%H:%M:%S")

    _, tgt_time = tgt_date.split('T')

    URL = "https://api.upbit.com/v1/trades/ticks"
    PARAMS = {
        "market" : market,
        "to": tgt_time,
        "count": max_per_attmp
    }

    for k, v in kwargs['params'].items():
        if v:
            PARAMS[k] = v

    try:
        response = requests.get(URL, params=PARAMS)
        response.raise_for_status()
        
        return response.json()

    except requests.exceptions.RequestException as e:  
        LOGGER.error(f"Error Fetching Data from UpBit : {e}")
        
        return None
    

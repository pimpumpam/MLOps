import datetime
import pandas as pd

from utils.utils import TIME_UNIT_DICT


def validate_missing_values(data):
    """
    데이터 유효성 검사.

    parameter
    ----------
    data(pandas.DataFrame): 유효성 검사 대상이 되는 dataframe.

    return
    ----------
    (bool): 데이터 무결성 여부. True이면 데이터 무결성 조건 충족.

    """
    return data.isnull().sum().sum() == 0


def validate_missing_timestamp(data, time_col, unit='minute', time_freq=1):
    """
    시계열 컬럼 유효성 검사.
    
    parameter
    ----------
    data(pandas.DataFrame): 유효성 대상이 되는 dataframe
    time_col(str):
    unit(str):
    time_freq(int):

    return
    ----------
    (bool): 데이터 무결성 여부. True이면 데이터 무결성 조건 충족.
    
    """
        
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])
        
    total_gaps = pd.date_range(
        start=data[time_col].min(),
        end=data[time_col].max(),
        freq=f'{time_freq}{TIME_UNIT_DICT[unit]}'
    )
    
    return len(data) == len(total_gaps)

def validate_duplicate_values(data):
    """
    데이터 중복 유효성 검사.
    
    parameter
    ----------
    data(pandas.DataFrame): 유효성 검사 대상이 되는 dataframe.
    
    return
    ----------
    (bool): 데이터 중복 여부. True이면 데이터 무결성 조건 충족.
    
    """
    
    return data.duplicated().sum() == 0

def fill_time_gaps(data, time_col, start_time, end_time, unit='minute', time_freq=1):
    """
    비어 있는 시간 정보 채우기.
    
    parameter
    ----------
    data(pandas.DataFrame): 
    time_col(str): 시간 관련 컬럼명
    start_time(str, datetime.datetime): 시간 범위의 마지막 시간 정보
    end_time(str, datetime.datetime): 시간 범위의 마지막 시간 정보
    unit(str): 채우려는 시간의 기준 단위. Defaults to 'minute'.
    time_freq(int): 채우려는 시간의 기준 단위. Defaults to 1.

    return
    ----------
    data(pandas.DataFrame): 
    
    """
    
    if isinstance(start_time, str):
        start_time = pd.to_datetime(start_time)
        
    if isinstance(end_time, str):
        end_time = pd.to_datetime(end_time)
        
    
    total_gaps = pd.date_range(
        start=start_time,
        end=end_time,
        freq=f'{time_freq}{TIME_UNIT_DICT[unit]}'
    )
    
    data = data.copy()
    data = data[~data[time_col].duplicated()]
    data = data.set_index(time_col)
    data = data.reindex(total_gaps)
    
    return data.reset_index(names=time_col)


def fill_missing_values(data, columns, how="mean", fill_value=None):
    """
    특정 컬럼들에 대한 결측값 처리

    parameter
    ----------
    data(pandas.DataFrame): 결측값 처리 대상 dataframe.
    columns(list): 결측값 처리 대상 컬럼.
    how(str): 결측값 처리 여부. mean, median, min, max 중 선택 가능.
    fill_value(dict): {column_name : fill_value}로 표현 된 dictionary
    """

    if not isinstance(columns, list):
        columns = [columns]

    data = data.copy()

    if fill_value is not None:
        for col in columns:
            data[col].fillna(fill_value, inplace=True)

        return data

    if how == "mean":
        for col in columns:
            data[col].fillna(data[col].mean(), inplace=True)
    elif how == "median":
        for col in columns:
            data[col].fillna(data[col].median(), inplace=True)

    elif how == "min":
        for col in columns:
            data[col].fillna(data[col].min(), inplace=True)

    elif how == "max":
        for col in columns:
            data[col].fillna(data[col].max(), inplace=True)

    return data

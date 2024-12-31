import pandas as pd

def aggregate_by_time(data, time_col, unit='minute', time_freq=5, **kwargs):
    """
    특정 시간을 기준으로 데이터 집계

    parameter
    ----------
    data(pandas.DataFrame): 집계 대상이 되는 dataframe
    time_col(str): Grouping에 사용 될 시간 컬럼 명
    unit(str): 시간 단위. minute, hour, day, week, month 가능.
    time_freq(int): 시간 주기. 할당 된 시간 주기 만큼 집계.
    kwargs
        group_cols(str, list): 시간 컬럼 외 grouping에 사용할 컬럼
    
    return
    ----------
    (pandas.DataFrame): 평균 값으로 집계 된 dataframe
    """

    # time meta
    time_unit_dict = {
        'minute' : 'T',
        'hour' : 'H',
        'day' : 'D',
        'week': 'W',
        'month': 'M'
    }

    group_cols = []
    group_cols.append(time_col)
    if 'group_cols' in kwargs:
        if not isinstance(kwargs['group_cols'], list):
            kwargs['group_cols'] = [kwargs['group_cols']]

        group_cols.extend(kwargs['group_cols'])    
    
    # copy data
    data = data.copy()

    # check & convert time column to datetime
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])

    # transform time
    data[time_col] = data[time_col].dt.floor(f'{time_freq}{time_unit_dict[unit]}')

    return data.groupby(group_cols).mean().reset_index(drop=True)


def amount_of_change_price(data, time_col, feature_col, unit='day', time_freq=1):
    """
    특정 시간 이전 대비 변화 산출.
    Argument 중 unit='day'이고 time_freq=1이면 현재 시점으로부터 1일 전 시점의 데이터의 차이 산출. 

    parameter
    ----------
    data(pandas.DataFrame): 변화량을 산출 할 대상이 되는 dataframe
    time_col(str): 시점 비교를 위해 사용 될 시간 컬럼 명
    feature_col(str, list): 변화값 산출을 위한 컬럼
    unit(str): 시간 단위. minute, hour, day, week, month 가능.
    time_freq(int): 시간 주기. 할당 된 시간 주기 만큼 집계.

    return
    ----------
    data(pandas.DataFrame): 

    """

    # time meta
    time_unit_dict = {
        'minute' : 'T',
        'hour' : 'H',
        'day' : 'D',
        'week': 'W',
        'month': 'M'
    }

    # dtype check
    if not isinstance(feature_col, list):
        feature_col = [feature_col]

    # copy data
    data = data.copy()

    # check & convert time column to datetime
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])

    # sort by timestamp
    data = data.sort_values(by=time_col).reset_index(drop=True)

    # calculate difference
    for col in feature_col:
        data[f'prev_{col}'] = data.set_index(time_col)[col].shift(freq=f'{time_freq}{time_unit_dict[unit]}')
        data[f'DIFF_{col}'] = data[col] - data[f'prev_{col}']

        data.drop(columns=f'prev_{col}')

    return data


def amount_of_change_rate(data, time_col, feature_col, unit='day', time_freq=1):
    """
    특정 시간 이전 대비 변화 비율 산출.
    Argument 중 unit='day'이고 time_freq=1이면 현재 시점으로부터 1일 전 시점의 데이터의 차이 비율 산출. 

    parameter
    ----------
    data(pandas.DataFrame): 변화량을 산출 할 대상이 되는 dataframe
    time_col(str): 시점 비교를 위해 사용 될 시간 컬럼 명
    feature_col(str, list): 변화값 산출을 위한 컬럼
    unit(str): 시간 단위. minute, hour, day, week, month 가능.
    time_freq(int): 시간 주기. 할당 된 시간 주기 만큼 집계.

    return
    ----------
    data(pandas.DataFrame): 

    """

    # time meta
    time_unit_dict = {
        'minute' : 'T',
        'hour' : 'H',
        'day' : 'D',
        'week': 'W',
        'month': 'M'
    }

    # dtype check
    if not isinstance(feature_col, list):
        feature_col = [feature_col]

    # copy data
    data = data.copy()

    # check & convert time column to datetime
    if not pd.api.types.is_datetime64_any_dtype(data[time_col]):
        data[time_col] = pd.to_datetime(data[time_col])
    
    # sort by timestamp
    data = data.sort_values(by=time_col).reset_index(drop=True)

    # calculate different ratio
    for col in feature_col:
        data[f'prev_{col}'] = data.set_index(time_col)[col].shift(freq=f'{time_freq}{time_unit_dict[unit]}')
        data[f'RATIO_{col}'] = data[col] / data[f'prev_{col}']

        data.drop(columns=f'prev_{col}')

    return data
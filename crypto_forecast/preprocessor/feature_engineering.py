import pandas as pd

def aggregate_by_time(data, time_col, unit='minute', time_freq=5, **kwargs):
    """
    특정 시간을 기준으로 데이터 집계

    parameter
    ----------
    data(pandas.DataFrame): 집계 대상이 되는 dataframe
    time_col(str): Grouping에 사용 될 시간 컬럼 명
    unit(str): 시간 단위. minute, hour, day 가능.
    time_freq(int): 시간 주기. 할당 된 시간 주기 만큼 집계.
    kwargs
        group_cols(str, list): 시간 컬럼 외 grouping에 사용할 컬럼
    
    return
    ----------
    (pandas.DataFrame): 평균 값으로 집계 된 dataframe
    """
    time_unit_dict = {
        'minute' : 'T',
        'hour' : 'H',
        'day' : 'D'
    }

    if 'group_cols' in kwargs:
        if not isinstance(kwargs['group_cols'], list):
            group_cols = list(kwargs['group_cols'])
        
        group_cols.append(time_col)
    
    data = data.copy()
    data[time_col] = pd.to_datetime(data[time_col])
    data[time_col] = data[time_col].dt.floor(f'{time_freq}{time_unit_dict[unit]}')

    return data.groupby(group_cols).mean().reset_index(drop=True)



def amount_of_change_price(data):
    """
    전일 동일 시간 대비 변화 금액 산출

    parameter
    ----------
    data(pandas.DataFrame): 변화량을 산출 할 대상이 되는 dataframe

    return
    ----------
    """

    data = data.copy()


def amount_of_change_rate(data):
    """
    전일 동일 시간 대비 변화 비율 산출

    parameter
    ----------
    data(pandas.DataFrame): 변화량을 산출 할 대상이 되는 dataframe

    return
    ----------
    """

    data = data.copy()
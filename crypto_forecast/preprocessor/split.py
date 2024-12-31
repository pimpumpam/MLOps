import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from utils.logger import setup_logger

LOGGER = setup_logger(__name__, 'train_workflow.log')


def split_train_test(data, train_ratio, test_ratio=None, **kwargs):
    """
    학습 및 검증 데이터 셋으로 분할.
    단순 비율을 통해 분할 하거나, 특정 시간을 기점으로 이전과 이후 시점을 각각 학습, 검증 데이터 셋으로 분할

    parameter
    ----------
    data(pandas.DataFrame): 분할 대상이 되는 데이터 셋
    train_ratio(float): 학습 데이터 셋 비율.
    test_ratio(float): 검증 데이터 셋 비율. Default: None
    kwargs
        time_col(str): 시간 관련 컬럼
        split_point(str, datetime): 시간 기준 train, test 분할 시 기준이 되는 시간 정보
    
    return
    ----------
    train_data(pandas.DataFrame)
    test_data(pandas.DataFrame)
    
    """
    
    if train_ratio is not None and test_ratio is None:
        train_ratio = train_ratio

    elif train_ratio is None and test_ratio is not None:
        train_ratio = 1-test_ratio

    elif train_ratio is not None and test_ratio is not None:
        if train_ratio+test_ratio != 1:
            LOGGER.error(f"Sum of argument \'train_ratio\' and \'test_ratio\' must be 1")
        elif train_ratio+test_ratio == 1:
            train_ratio = train_ratio

    # sort by time column
    if 'time_col' in kwargs:
        if not pd.api.types.is_datetime64_any_dtype(data[kwargs['time_col']]):
            data[kwargs['time_col']] = pd.to_datetime(data[kwargs['time_col']])

        data = data.sort_values(by=kwargs['time_col']).reset_index(drop=True)

    if 'split_point' in kwargs:
        if 'time_col' not in kwargs:
            LOGGER.error(f"To split the data based on time, you must assign the name of the time-related column to the \'time_col\' argument.")

        elif isinstance(kwargs['split_point'], str):
            split_point = pd.to_datetime(kwargs['split_point'])

        train_data = data[data[kwargs['time_col']] <= split_point]
        test_data = data[data[kwargs['time_col']] > split_point]

        return train_data, test_data
        
    else:
        split_point = int(len(data) * train_ratio)

        train_data = data.iloc[:split_point]
        test_data = data.iloc[split_point:]

        return train_data, test_data



def split_sliding_window(data, feature_col, input_seq_len, label_seq_len=1, **kwargs):
    """
    모델 학습에 횔용 할 input과 label 데이터를 위한 sliding window 적용 

    parameter
    ----------
    data(pandas.DataFrame): 
    feature_col(str, list): Feature로 활용할 컬럼 정보.
    input_seq_len(int): Input 데이터 셋의 time sequence 길이.
    label_seq_len(int): Label 데이터 셋의 time sequence 길이. Default=1
    kwargs
        time_col(str): 데이터 셋 내 시간 관련 컬럼.

    return
    ----------
    X(numpy.ndarray): Input 데이터로 활용하기 위한 sliding window 적용 결과.
    y(numpy.ndarray): Label 데이터로 활용하기 위한 sliding window 적용 결과.

    """
    
    # dtype check
    if not isinstance(feature_col, list):
        feature_col = [feature_col]

    # sort by time column
    if 'time_col' in kwargs:
        if not pd.api.types.is_datetime64_any_dtype(data[kwargs['time_col']]):
            data[kwargs['time_col']] = pd.to_datetime(data[kwargs['time_col']])

        data = data.sort_values(by=kwargs['time_col']).reset_index(drop=True)

    # data sampling
    data_arr = data[feature_col].values

    # set sequence length
    seq_len = input_seq_len + label_seq_len

    # apply sliding window
    window_data = sliding_window_view(data_arr, seq_len)

    # set inputs and labels
    X = window_data[:, :input_seq_len]
    y = window_data[:, input_seq_len:]

    return X, y
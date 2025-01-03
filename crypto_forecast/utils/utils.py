import os

from itertools import product
from typing import Sequence, cast

PROGRESS_BAR_FORMAT = '{l_bar}{bar:10}{r_bar}'
TIME_UNIT_DICT = {
        'minute' : 'T',
        'hour' : 'H',
        'day' : 'D',
        'week': 'W',
        'month': 'M'
    }

def load_spec_from_config(cfg_name):
    """
    Config 파일에서 관련 정보 호출

    parameter
    ----------
    cfg_name(str): config 파일명

    return
    ----------
    meta_spec(class): 메타에 대한 config 정보
    loader_spec(class): 데이터 불러오기에 대한 config 정보
    preprocessor_spec(class): 전처리에 대한 config 정보
    model_spec(class): 모델에 대한 config 정보
    hyp_spec(class): 하이퍼파라미터에 대한 config 정보
    evlauate_spec(class): 모델 평가에 대한 대한 config 정보
    """
    
    meta_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgMeta
    
    database_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgDatabase
    
    loader_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgLoader
        
    preprocessor_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgPreprocessor
    
    model_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgModel
    
    hyp_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgHyperParameter
    
    evaluate_spec = __import__(
        f"configs.{cfg_name}", fromlist=cast(Sequence[str], [None])
    ).CfgEvaluate

    return meta_spec, database_spec, loader_spec, preprocessor_spec, model_spec, hyp_spec, evaluate_spec


def create_seq_values(table_info, data):
    """
    테이블 내 값 적재를 위한 iterable 변수 생성

    parameter
    ----------
    table_info(dict): 컬럼 명, 타입 등으로 구성 된 테이블 정보
    data(list): 관측값 정보가 다수의 dictionary로 구성 된 list
    
    return
    ----------
    param_seq(list): 

    """

    param_seq = []
    for attr in data:
        row = [attr[col['source']] for col in table_info['columns']]
        param_seq.append(row)
    
    return param_seq

def hyperparameter_combination(cfg_hyp):
    attributes = {attr: getattr(cfg_hyp, attr) for attr in dir(cfg_hyp) if not attr.startswith("__") and not callable(getattr(cfg_hyp, attr))}
    hyps, vals = attributes.keys(), attributes.values()
    combinations = [dict(zip(hyps, comb)) for comb in product(*vals)]
    
    return combinations
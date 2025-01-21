def create_seq_values(table_info, data, **kwargs):
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

    if 'column_key' in kwargs:
        column_key = kwargs['column_key']
    else:
        column_key = 'source'
    
    param_seq = []
    for attr in data:
        row = [attr[col[column_key]] for col in table_info['columns']]
        param_seq.append(row)
    
    return param_seq
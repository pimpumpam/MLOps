def validate_no_missing_values(data):
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

import os
import pickle
import collections

import sklearn
import sklearn.preprocessing

from utils.logger import setup_logger


LOGGER = setup_logger(__name__, 'train_workflow.log')


class MultiColumnLabelEncoder:
    
    def __init__(self, encoder_name):
        
        """
        Initializer
        
        각 컬럼에 적용 될 encoder를 딕셔너리 형태로 구현
        dict = {columns명 : 각 columns에 fit 된 encoder} 

        parameter
        ----------
        encoder(str): 각 컬럼에 적용 할 encoder 명.
                      sklearn.preprocessing.OneHotEncoder/OrdinalEncoder/LabelEncoder 사용 가능.
        
        """
        self.encoder_dict = collections.defaultdict(eval(encoder_name))
        
    
    def transform(self, data, columns, inplace=False):
        if not isinstance(columns, list):
            columns = [columns]
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(lambda x: self.encoder_dict[x.name].transform(x))
            
            return data
        
        else:
            data[columns] = data[columns].apply(lambda x: self.encoder_dict[x.name].transform(x))
            
        LOGGER.info(f"Complete transformation using LabelEncoder")
    
    
    def fit_transform(self, data, columns, inplace=False, save_pkl=False, **kwargs):
        
        """
        Argument로 주어진 multi column의 각 컬럼에 대해 Label Encoding 수행
        
        parameter
        ---------
        data(pandas.DataFrame): Label Encoding을 적용할 Column이 포함된 DataFrame
        columns(list): DataFrame 내 Label Encoding을 적용할 컬럼명
        inplace(boolean): Argument로 사용된 DataFrame 변환 유지 여부
        save_pkl(boolean): LabelEncoder를 pkl 형식으로 저장 할지에 대한 여부
        kwargs:
            save_path(str): LabelEncoder 객체 저장 경로
        
        return
        ----------
        data(pandas.DataFrame): Label Encoding이 적용 된 DataFrame
        
        """
        
        if not isinstance(columns, list):
            columns = [columns]
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(lambda x: self.encoder_dict[x.name].fit_transform(x))
            
            return data
        
        else:
            data[columns] = data[columns].apply(lambda x: self.encoder_dict[x.name].fit_transform(x))
            
        LOGGER.info(f"Complete fitting & transformation using LabelEncoder")
        
        
        if save_pkl:
            with open(
                os.path.join(kwargs['save_path'], f"{kwargs['save_name']}.pkl"), 'wb') as f:
                pickle.dump(self.encoder_dict, f)
                
            LOGGER.info(f"Complete save \"LabelEncoder\"")
    
    def inverse_transform(self, data, columns, inplace=False):
        
        """
        Multi Columns에 대해 변환 된 Label Encoder 정보를 기반으로 원래 형태로 역변환
        
        parameter
        ----------
        data(pandas.DataFrame): 역변환을 적용할 Column이 포함된 DataFrame
        columns(list): 역변환을 적용할 Column 명으로 구성된 List
        inplace(boolean): Argument로 사용된 DataFrame 변환 유지 여부
        
        return
        ----------
        data(pandas.DataFrame): 역변환이 적용 된 DataFrame
        
        """
        
        if not isinstance(columns, list):
            columns = [columns]
            
        if not all(key in self.encoder_dict for key in columns):
            LOGGER.error(f"One of column in {columns} is not encoded")
            raise KeyError(f"One of column in {columns} is not encoded")
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(lambda x: self.encoder_dict[x.name].inverse_transform(x))
            
            return data
        
        else:
            data[columns] = data[columns].apply(lambda x: self.encoder_dict[x.name].inverse_transform(x))

        LOGGER.info(f"Complete inverse transformation using LabelEncoder")


class MultiColumnScaler:
    def __init__(self, scaler_name):
        self.scaler_name = scaler_name
        self.scaler_dict = collections.defaultdict(eval(f"sklearn.preprocessing.{scaler_name}"))
        
    def transform(self, data, columns, inplace=False):
        
        if not isinstance(columns, list):
            columns = [columns]
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].transform(x)
                )
        
        else:
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].transform(x)
            )
            
    
    def fit_transform(self, data, columns, inplace=False, save_pkl=False, **kwargs):
        if not isinstance(columns, list):
            columns = [columns]
            
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].fit_transform(x.values.reshape(-1, 1)).flatten()
            )
            
            return data
    
        else:
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].fit_transform(x.values.reshape(-1, 1)).flatten()
            )
            
        if save_pkl:
            with open(os.path.join(kwargs['save_path'], f"{self.scaler_name}_{kwargs['save_name']}.pkl"), 'wb') as f:
                pickle.dump(self.scaler_dict, f)
                
            LOGGER.info(f"Complete save \"{self.scaler_name}\"")
            
            
    def inverse_transform(self, data, columns, inplace=False):
        if not isinstance(columns, list):
            columns = [columns]
            
        if not all(key in self.scaler_dict for key in columns):
            raise KeyError(f"One of column in {columns} is not scaled")
        
        if not inplace:
            data = data.copy()
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].inverse_transform(x.values.reshape(-1, 1)).flatten()
            )
            
            return data

        else:
            data[columns] = data[columns].apply(
                lambda x: self.scaler_dict[x.name].inverse_transform(x.values.reshape(-1, 1)).flatten()
            )


        
# class MultiColumnScaler:
    
#     def __init__(self, scaler_name):
        
#         """
#         Initializer
        
#         paramater
#         ----------
#         scaler_kind(str): 각 Column에 적용 할 Scailer 명.
#                           sklearn.preprocessing.StandardScaler/MinMaxSclaer 사용 가능.
        
#         """
        
#         self.scaler = eval(scaler_name)()
        
    
#     def transform(self, data, columns, inplace=False):
#         if not isinstance(columns, list):
#             columns = [columns]
            
#         if not inplace:
#             data = data.copy()
#             data[columns] = self.scaler.transform(data[columns])
            
#             return data
        
#         else:
#             data[columns] = self.scaler.transform(data[columns])
    
#         LOGGER.info(f"✅ Complete transformation using {type(self.scaler).__name__}")
        
    
#     def fit_transform(self, data, columns, inplace=False, save_pkl=False, **kwargs):
        
#         """
#         Argument로 주어진 multi column의 각 컬럼에 대해 Scaler 적용
        
#         parameter
#         ---------
#         data(pandas.DataFrame): Scaling 할 Column이 포함된 DataFrame
#         columns(list): DataFrame 내 Scaler를 적용할 컬럼명
#         inplace(boolean): Argument로 사용된 DataFrame 변환 유지 여부
#         save_pkl(boolean): Scaler 객체를 pkl 형식으로 저장 할지에 대한 여부
#         kwargs:
#             save_path(str): Scaler 객체 저장 경로
        
#         return
#         ----------
#         data(pandas.DataFrame): Label Encoding이 적용 된 DataFrame
        
#         """
            
#         if not isinstance(columns, list):
#             columns = [columns]
            
#         if not inplace:
#             data = data.copy()
#             data[columns] = self.scaler.fit_transform(data[columns])
#             return data
        
#         else:
#             data[columns] = self.scaler.fit_transform(data[columns])
            
#         LOGGER.info(f"Complete fitting & transformation using {type(self.scaler).__name__}")
        
#         if save_pkl:
#             with open(os.path.join(kwargs['save_path'], f"{type(self.scaler).__name__}_{kwargs['save_name']}.pkl"), 'wb') as f:
#                 pickle.dump(self.scaler, f)
                
#             LOGGER.info(f"Complete save \"{type(self.scaler).__name__}\"")
            
            
#     def inverse_transform(self, data, columns, inplace=False):
        
#         """
#         Scaler 정보를 기반으로 Multi Columns 정보 역변환
        
#         parameter
#         ----------
#         data(pandas.DataFrame): 역변환을 적용할 Column이 포함된 DataFrame
#         columns(list): 역변환을 적용할 Column 명으로 구성된 List
#         inplace(boolean): Argument로 사용된 DataFrame 변환 유지 여부
        
#         return
#         ----------
#         data(pandas.DataFrame): 역변환이 적용 된 DataFrame
        
#         """
        
#         if not isinstance(columns, list):
#             columns = [columns]
            
#         if not inplace:
#             data = data.copy()
#             data[columns] = self.scaler.inverse_transform(data[columns])
            
#             return data
        
#         else:
#             data[columns] = self.scaler.inverse_transform(data[columns])
            
#         LOGGER.info(f"Complete inverse transformation using {type(self.scaler).__name__}")
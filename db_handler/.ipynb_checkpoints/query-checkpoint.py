import pandas as pd

class Query:
    
    @staticmethod
    def is_table_exists(table_info):
        scheme = table_info['scheme']
        table = table_info['table']
    
        return f"SELECT 1 FROM sqlite_master WHERE 1=1 AND type='table' AND name = '{scheme}_{table}';"
    
    @staticmethod
    def create_table(table_info):
        
        scheme = table_info['scheme']
        table = table_info['table']
        columns = ", ".join([f"{col['name']} {col['type']}" for col in table_info['columns']])

        return f"CREATE TABLE IF NOT EXISTS {scheme}_{table} (id INTEGER PRIMARY KEY, {columns});"
    
    @staticmethod
    def insert_data_to_table(table_info):

        scheme = table_info['scheme']
        table = table_info['table']
        columns = ", ".join([col['name'] for col in table_info['columns']])
        values = ", ".join(['?'] * len([col['name'] for col in table_info['columns']]))

        return f"INSERT INTO {scheme}_{table} ({columns}) VALUES ({values});"
    
    
    @staticmethod
    def drop_dulicate_row(table_info):
        
        scheme = table_info['scheme']
        table = table_info['table']
        columns = ", ".join([f"{col['name']}" for col in table_info['columns']])
        
        return f"""WITH CTE AS (
                        SELECT *,
                        ROW_NUMBER() OVER (
                            PARTITION BY {columns}
                            ORDER BY id
                        ) AS rn
                        FROM {scheme}_{table}
                    )
                    DELETE FROM {scheme}_{table}
                    WHERE id IN (
                        SELECT id
                        FROM CTE
                        WHERE rn>1
                    )
                    ;
                    """   
    
    @staticmethod
    def get_recent_timestamp(table_info, **kwargs):
        
        if 'time_col' in kwargs:
            time_col = kwargs['time_col']
            
        else:
            time_col = 'KST_TIME'
        
        scheme = table_info['scheme']
        table = table_info['table']
        
        return f"SELECT max({time_col}) FROM {scheme}_{table};"
    
    
    @staticmethod
    def dataframe_to_table(table_info, data, conn, **kwargs):
        """
        데이터프레임을 데이터베이스 내 테이블로 적재
        
        parameter
        ----------
        table_info(dict): 스키마, 테이블, 컬럼 정보 등이 있는 테이블 메타 정보
        data(pandas.DataFrame): 데이터베이스 내 테이블로 적재 대상이 되는 데이터프레임
        
        return
        ----------
        None
        """
        
        scheme = table_info['scheme']
        table = table_info['table']
        
        if 'table_name_suffix' in kwargs:
            table = table + '_' + kwargs['table_name_suffix']
        
        if 'table_exists_handling' not in kwargs:
            exist_handling = 'append'
        else:
            exist_handling = kwargs['table_exists_handling']
                
        data.to_sql(
            f'{scheme}_{table}', 
            conn, 
            if_exists=exist_handling, 
            index=True,
            index_label='id'
        )
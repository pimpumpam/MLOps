import sqlite3
import pandas as pd

class SQLiteDBManager:
    def __init__(self, db_path):
        """
        Initializer

        parameter
        ----------
        db_path(str): 데이터베이스 경로

        return
        ----------
        None
        
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def _get_all_table_name_(self):
        """
        데이터베이스 내 모든 테이블 명 조회

        parameter
        ----------
        None

        return
        ----------
        None

        """
        query = """SELECT name FROM sqlite_master WHERE type='table';"""
        return self.cursor.fetchall(query)

    def execute_query(self, query):
        """
        쿼리문 실행

        parameter
        ----------
        query(str): 실행 쿼리문

        return 
        ----------
        None
        """
        self.cursor.execute(query)
        self.conn.commit()

    def execute_many_query(self, query, param_seq):
        """
        동일한 SQL 문을 여러 데이터 세트에 대해 실행

        parameter
        ----------
        query(str): 실행 쿼리문
        param_seq(tuple, list): 반복 적용 할 대상
        
        return
        ----------
        None
        """
        self.cursor.executemany(query, param_seq)
        self.conn.commit()

    def fetch_all(self, query):
        """
        쿼리문 실행 결과 반환

        parameter
        ----------
        query(str): 실행 쿼리문

        return
        ----------
        (list)
        
        """
        self.cursor.execute(query)

        return self.cursor.fetchall()
    
    def fetch_to_dataframe(self, query):
        """
        쿼리문 실행 결과를 pandas.DataFrame으로 반환

        parameter
        ----------
        query(str): 실행 쿼리문

        return
        ----------
        data(pandas.DataFrame)
        """
        data = pd.read_sql_query(query, self.conn)
        
        return data
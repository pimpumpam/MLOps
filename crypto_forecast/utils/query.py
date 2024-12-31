class BronzeLayerQuery:
    @staticmethod
    def create_table(table_info):
        
        scheme = table_info['scheme']
        table = table_info['table']
        columns = ", ".join([f"{col['name']} {col['type']}" for col in table_info['columns']])

        return f"CREATE TABLE IF NOT EXISTS {scheme}_{table} ({columns});"
    
    @staticmethod
    def insert_data_to_table(table_info):

        scheme = table_info['scheme']
        table = table_info['table']
        columns = ", ".join([col['name'] for col in table_info['columns']])
        values = ", ".join(['?'] * len([col['name'] for col in table_info['columns']]))

        return f"INSERT INTO {scheme}_{table} ({columns}) VALUES ({values});"


class SilverLayerQuery:

    @staticmethod
    def aggregate_by_time_unit(table_info, time_unit):
        
        scheme = table_info['target']['scheme']
        table = table_info['target']['table']
        columns = ", ".join([col['name'] for col in table_info['columns']])
        column_type = ", ".join([f"{col['name']} {col['type']}" for col in table_info['columns']])

        return f"""
                CREATE TABLE IF NOT EXISTS {scheme}_{table}_{time_unit} ({column_type})
                INSERT INTO {scheme}_{table}_{time_unit} ({columns})
                SELECT
                    MARKET AS MARKET,
                    strftime('%Y-%m-%d %H:', KST_TIME) || 
                        printf('%02d', CAST(strftime('%M', KST_TIME) AS INTEGER) / {time_unit} * {time_unit} + {time_unit}) || 
                        strftime(':%S', KST_TIME) AS KST_TIME,
                    AVG(OPEN_PRICE) AS OPEN_PRICE,
                    AVG(CLOSE_PRICE) AS CLOSE_PRICE,
                    AVG(LOW_PRICE) AS LOW_PRICE,
                    AVG(HIGH_PRICE) AS HIGH_PRICE,
                    AVG(ACC_TRADE_PRICE) AS ACC_TRADE_PRICE,
                    AVG(ACC_TRADE_VOLUME) AS ACC_TRADE_VOLUME
                FROM {table_info['source']['scheme']}_{table_info['source']['table']}
                GROUP BY MARKET, KST_TIME
                ORDER BY KST_TIME
                ;
                """


class GoldLayerQuery:
    print("Gold-layer 쿼리 코드 개발 중")
import sqlite3
import os
import pandas as pd

def table_list_query(conn):
    #Listar tablas
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    tables = cursor.fetchall()

    print("Tablas en la base de datos:")
    for t in tables:
        print(t)


def bar_mad_query(conn):
    #Query Barça vs Madrid
    query = """
    SELECT 
        m.date,
        t1.team_long_name AS home_team,
        t2.team_long_name AS away_team,
        m.home_team_goal,
        m.away_team_goal
    FROM Match m
    JOIN Team t1 ON m.home_team_api_id = t1.team_api_id
    JOIN Team t2 ON m.away_team_api_id = t2.team_api_id
    WHERE 
        (t1.team_long_name = 'FC Barcelona' AND t2.team_long_name = 'Real Madrid CF')
        OR
        (t1.team_long_name = 'Real Madrid CF' AND t2.team_long_name = 'FC Barcelona')
    ORDER BY m.date;
    """

    df = pd.read_sql(query, conn)

    print(df)

def examine_table(conn, table_name):
    query = f"SELECT * FROM {table_name} LIMIT 5;"
    df = pd.read_sql(query, conn)
    print(f"Primeras filas de la tabla {table_name}:")
    print(df)

def print_columns(conn, table_name):
    query = f"PRAGMA table_info({table_name});"
    df = pd.read_sql(query, conn)
    print(f"Columnas de la tabla {table_name}:")
    print(df[['name', 'type']])


# Construir ruta absoluta segura
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "data", "database.sqlite")
conn = sqlite3.connect(db_path)

#table_list_query(conn)
examine_table(conn, 'Team_Attributes')
#print_columns(conn, 'Match')

"""('sqlite_sequence',)
('Player_Attributes',)
('Player',)
('Match',)
('League',)
('Country',)
('Team',)
('Team_Attributes',)"""
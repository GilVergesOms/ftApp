# ftApp/queries.py
import pandas as pd

def get_teams(conn):
    """Devuelve lista de equipos"""
    return pd.read_sql("SELECT team_long_name FROM Team ORDER BY team_long_name", conn)

def get_team_detail(conn, team_name):
    """
    Devuelve info de un equipo: partidos jugados, goles, etc.
    """
    query = f"""
    SELECT 
        DATE(m.date) AS date,
        t1.team_long_name AS "home_team",
        t2.team_long_name AS "away_team",
        (m.home_team_goal || '-' || m.away_team_goal) AS "Score",
        l.name AS "Competition",
        m.season AS "Season"
    FROM Match m
    JOIN Team t1 ON m.home_team_api_id = t1.team_api_id
    JOIN Team t2 ON m.away_team_api_id = t2.team_api_id
    JOIN League l ON m.league_id = l.id
    WHERE t1.team_long_name='{team_name}' OR t2.team_long_name='{team_name}'
    ORDER BY m.date
    """
    return pd.read_sql(query, conn)

def get_matches(conn, team=None, rival=None, season=None):
    """Devuelve partidos filtrando por equipo y rival"""
    query = """
        SELECT 
            DATE(m.date) AS Date,
            t1.team_long_name AS "home_team",
            t2.team_long_name AS "away_team",
            (m.home_team_goal || '-' || m.away_team_goal) AS Score,
            l.name AS Competition,
            m.season AS Season
        FROM Match m
        JOIN Team t1 ON m.home_team_api_id = t1.team_api_id
        JOIN Team t2 ON m.away_team_api_id = t2.team_api_id
        JOIN League l ON m.league_id = l.id
        WHERE 1=1
        """
    if team:
        query += f" AND (t1.team_long_name='{team}' OR t2.team_long_name='{team}')"
    if rival:
        query += f" AND (t1.team_long_name='{rival}' OR t2.team_long_name='{rival}')"
    if season:
        query += f" AND m.season='{season}'"
    query += " ORDER BY m.date desc"
    return pd.read_sql(query, conn)
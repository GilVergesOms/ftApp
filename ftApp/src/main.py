import streamlit as st
from utils import get_db_connection
from queries import get_teams, get_matches
import pandas as pd
import altair as alt

st.set_page_config(page_title="Football Dashboard MVP", layout="wide")
st.title("📊 Football Dashboard MVP - Visual H2H")

# ------------------ CONEXIÓN ------------------
conn = get_db_connection()

# ------------------ FILTROS ------------------
teams_df = get_teams(conn)
teams = teams_df['team_long_name'].tolist()

seasons_df = conn.execute("SELECT DISTINCT season FROM Match ORDER BY season DESC").fetchall()
seasons = [s[0] for s in seasons_df]

team = st.sidebar.selectbox("Selecciona tu equipo", [""] + teams)
rival = st.sidebar.selectbox("Selecciona rival (opcional)", [""] + teams)
season = st.sidebar.selectbox("Selecciona temporada (opcional)", [""] + seasons)

# ------------------ ESTADO ------------------
if 'selected_team' not in st.session_state:
    st.session_state['selected_team'] = None

# ------------------ FUNCIONES ------------------
def mostrar_detalle_equipo(team_name):
    st.subheader(f"Detalle del equipo: {team_name}")
    st.write("Aquí puedes añadir más estadísticas, gráficos o atributos del equipo.")
    if st.button("Volver al listado de partidos"):
        st.session_state['selected_team'] = None

def calcular_resultados(df, team_name):
    # Devuelve DataFrame con columnas: Resultado, Count
    res = []
    for idx, row in df.iterrows():
        h_goal, a_goal = map(int, row['Score'].split('-'))
        if row['home_team'] == team_name:
            if h_goal > a_goal: res.append('W')
            elif h_goal == a_goal: res.append('D')
            else: res.append('L')
        elif row['away_team'] == team_name:
            if a_goal > h_goal: res.append('W')
            elif a_goal == h_goal: res.append('D')
            else: res.append('L')
    summary = pd.DataFrame(pd.Series(res).value_counts()).reset_index()
    summary.columns = ['Resultado','Count']
    return summary

def calcular_goles(df, team_name):
    # Devuelve DataFrame para gráfico de goles
    home = df['home_team'] == team_name
    away = df['away_team'] == team_name
    gf_home = df.loc[home, 'Score'].str.split('-').str[0].astype(int).sum()
    ga_home = df.loc[home, 'Score'].str.split('-').str[1].astype(int).sum()
    gf_away = df.loc[away, 'Score'].str.split('-').str[1].astype(int).sum()
    ga_away = df.loc[away, 'Score'].str.split('-').str[0].astype(int).sum()
    data = pd.DataFrame({
        'Tipo': ['GF Local','GC Local','GF Visitante','GC Visitante'],
        'Goles':[gf_home, ga_home, gf_away, ga_away]
    })
    return data

# ------------------ MAIN ------------------
if st.session_state['selected_team']:
    mostrar_detalle_equipo(st.session_state['selected_team'])
else:
    if st.sidebar.button("Buscar partidos"):
        if not team:
            st.warning("Selecciona al menos un equipo")
        else:
            df = get_matches(conn,
                             team=team,
                             rival=rival if rival else None,
                             season=season if season else None)

            if df.empty:
                st.info("No se encontraron partidos.")
            else:
                st.subheader(f"Partidos encontrados: {len(df)}")
                
                # Contenedor horizontal: izquierda = tabla, derecha = resumen visual
                left, right = st.columns([3,1])

                # ------------------ TABLA ------------------
                with left:
                    # Encabezado
                    col_date, col_home, col_score, col_away, col_comp, col_season = st.columns([1.5,2,1,2,2,1])
                    col_date.markdown("**Date**")
                    col_home.markdown("**Home Team**")
                    col_score.markdown("**Score**")
                    col_away.markdown("**Away Team**")
                    col_comp.markdown("**Competition**")
                    col_season.markdown("**Season**")

                    for idx, row in df.iterrows():
                        col_date, col_home, col_score, col_away, col_comp, col_season = st.columns([1.5,2,1,2,2,1])
                        col_date.write(row['Date'].split(' ')[0])
                        if col_home.button(row['home_team'], key=f"home_{idx}"):
                            st.session_state['selected_team'] = row['home_team']
                        col_score.write(row['Score'])
                        if col_away.button(row['away_team'], key=f"away_{idx}"):
                            st.session_state['selected_team'] = row['away_team']
                        col_comp.write(row['Competition'])
                        col_season.write(row['Season'])
                
                # ------------------ RESUMEN VISUAL ------------------
                with right:
                    st.subheader(f"H2H: {team}" + (f" vs {rival}" if rival else ""))

                    # Resultados
                    res_df = calcular_resultados(df, team)
                    st.markdown("**Resultados:**")
                    chart_res = alt.Chart(res_df).mark_bar().encode(
                        x='Resultado',
                        y='Count',
                        color=alt.Color('Resultado', scale=alt.Scale(domain=['W','D','L'], range=['green','grey','red']))
                    )
                    st.altair_chart(chart_res, use_container_width=True)

                    # Goles
                    goles_df = calcular_goles(df, team)
                    st.markdown("**Goles:**")
                    chart_goles = alt.Chart(goles_df).mark_bar().encode(
                        x='Tipo',
                        y='Goles',
                        color='Tipo'
                    )
                    st.altair_chart(chart_goles, use_container_width=True)

# ------------------ CERRAR CONEXIÓN ------------------
conn.close()
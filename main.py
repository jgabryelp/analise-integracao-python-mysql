#importação das bibliotecas
from sqlalchemy import URL, create_engine
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv() 

#configurando a conexão
try:
    senha = st.secrets['MYSQL_PASSWORD']
except:
    senha = os.getenv('MYSQL_PASSWORD')

conexao = create_engine(
    URL.create(
        drivername='mysql+pymysql',
        username='avnadmin',
        password=senha,
        host='mysql-82f184a-joaogabryelcaldeirap-a5a5.j.aivencloud.com',
        port=11978,
        database='defaultdb'
    ),
    connect_args={
        'ssl': {'ca': str(Path('config/ca.pem').resolve())}}
)


#ranking dos artistas com pelo menos 5 músicas, ordenados pela média de popularidade
artistasmaispopulares = """ 
SELECT CASE WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ';') - 1)   -- selecionando apenas o artista principal da faixa
ELSE tks.artists
END AS "artist",  AVG(tdt.popularity) AS "avg_popularity"       -- calculando a média de popularidade
FROM tracks AS tks INNER JOIN tracksdetails AS tdt        -- relacionando as informações das duas tabelas
ON tks.track_id = tdt.track_id                     -- relacionando as tabelas pelas colunas correspondentes
GROUP BY CASE 
        WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ';') - 1)   -- repetindo a expressão para agrupar pelo artista principal
        ELSE tks.artists
    END 
HAVING COUNT(tks.track_name) >= 5 ORDER BY avg_popularity DESC LIMIT 12;   -- filtrando artistas com pelo menos 5 músicas e ordenando pela média de popularidade
"""
tabelaartistasmaispopulares = pd.read_sql_query(artistasmaispopulares, conexao) #criando uma tabela do Pandas com os dados
print(tabelaartistasmaispopulares, '\n')


#gêneros mais populares
generosmaispopulares = """
SELECT tks.track_genre AS "genre", COUNT(*) AS "tracks_quantity", 
CONCAT(ROUND((SUM(tdt.popularity >= 80) / COUNT(*) * 100), 2), '%%') AS "popular_percent"  -- selecionando o gênero e calculando a quantidade e o percentual de músicas populares
FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id   -- relacionando as duas tabelas
GROUP BY genre ORDER BY popular_percent DESC LIMIT 14;  -- agrupando para que cada gênero apareça uma única vez
"""
tabelagenerosmaispopulares = pd.read_sql_query(generosmaispopulares, conexao)
print(tabelagenerosmaispopulares, '\n')


#artistas mais populares de cada gênero
artistasporgenero = """
WITH top_genres AS (   -- criando a CTE que armazena os gêneros mais populares (identificados na consulta anterior)
    SELECT tks.track_genre AS "genre"
    FROM tracks AS tks INNER JOIN tracksdetails AS tdt   
    ON tks.track_id = tdt.track_id
    GROUP BY genre
    ORDER BY (SUM(tdt.popularity >= 80) / COUNT(*)) DESC LIMIT 14
),

artist_avg AS (
    SELECT tks.track_genre AS genre, CASE WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ';') - 1)   -- selecionando apenas o artista principal da faixa
    ELSE tks.artists  -- selecionando o artista principal de cada faixa
    END AS "artist", 
    ROUND(AVG(tdt.popularity), 2) AS avg_popularity -- calculando a média de popularidade
    FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id
    INNER JOIN top_genres AS tg ON tks.track_genre = tg.genre  -- relacionando as duas tabelas principais com a CTE dos gêneros mais populares
    GROUP BY genre, artist
),

ranked_artists AS (
    SELECT artist, genre, avg_popularity, 
    ROW_NUMBER() OVER -- função de janela para numerar os artistas dentro de cada gênero pela média de popularidade
    (PARTITION BY genre ORDER BY avg_popularity DESC) AS ranking 
    FROM artist_avg
)

SELECT
    genre, CASE WHEN INSTR(ranked_artists.artist, ';') > 0 THEN LEFT(ranked_artists.artist, INSTR(ranked_artists.artist, ';') - 1)   -- selecionando apenas o artista principal da faixa
           ELSE ranked_artists.artist  -- selecionando apenas o artista principal da faixa
           END AS "artist",
    avg_popularity
    FROM ranked_artists
    WHERE ranking = 1 -- selecionando o artista com maior média de popularidade em cada gênero
    ORDER BY avg_popularity DESC;
"""
tabelaartistasporgenero = pd.read_sql_query(artistasporgenero, conexao)
print(tabelaartistasporgenero, '\n')


#características das músicas mais populares vs menos populares
caracteristicasporpopularidade = """
WITH toppopular AS ( SELECT *
FROM tracksdetails              -- CTE contendo as 20 músicas mais populares
ORDER BY popularity DESC
LIMIT 20
),
bottompopular AS (SELECT *
FROM tracksdetails              -- CTE contendo as 20 músicas menos populares
ORDER BY popularity ASC
LIMIT 20
)

-- calculando a média de cada característica para os grupos de músicas mais e menos populares
SELECT 'avg_duration_ms' AS feature,
ROUND((SELECT AVG(duration_ms) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(duration_ms) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(duration_ms) FROM toppopular) - (SELECT AVG(duration_ms) FROM bottompopular)) 
          / NULLIF((SELECT AVG(duration_ms) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL  -- unindo os resultados das diferentes características em linhas

SELECT 'avg_danceability',
ROUND((SELECT AVG(danceability) FROM toppopular), 2), 
ROUND((SELECT AVG(danceability) FROM bottompopular), 2),
CONCAT(
    ROUND((((SELECT AVG(danceability) FROM toppopular) - (SELECT AVG(danceability) FROM bottompopular)) 
          / NULLIF((SELECT AVG(danceability) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL

SELECT 'avg_energy',
ROUND((SELECT AVG(energy) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(energy) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(energy) FROM toppopular) - (SELECT AVG(energy) FROM bottompopular)) 
          / NULLIF((SELECT AVG(energy) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL

SELECT 'avg_loudness',
ROUND((SELECT AVG(loudness) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(loudness) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(loudness) FROM toppopular) - (SELECT AVG(loudness) FROM bottompopular)) 
          / NULLIF((SELECT AVG(loudness) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL

SELECT 'avg_speechiness',
ROUND((SELECT AVG(speechiness) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(speechiness) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(speechiness) FROM toppopular) - (SELECT AVG(speechiness) FROM bottompopular)) 
          / NULLIF((SELECT AVG(speechiness) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL

SELECT 'avg_acousticness',
ROUND((SELECT AVG(acousticness) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(acousticness) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(acousticness) FROM toppopular) - (SELECT AVG(acousticness) FROM bottompopular)) 
          / NULLIF((SELECT AVG(acousticness) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL

SELECT 'avg_valence',
ROUND((SELECT AVG(valence) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(valence) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(valence) FROM toppopular) - (SELECT AVG(valence) FROM bottompopular)) 
          / NULLIF((SELECT AVG(valence) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
UNION ALL

SELECT 'avg_tempo',
ROUND((SELECT AVG(tempo) FROM toppopular), 2), 
ROUND((SELECT AVG(tempo) FROM bottompopular), 2),
CONCAT(
    ROUND((((SELECT AVG(tempo) FROM toppopular) - (SELECT AVG(tempo) FROM bottompopular)) 
          / NULLIF((SELECT AVG(tempo) FROM bottompopular), 0)) * 100, 2 ),'%%') AS "percent_difference" 
"""
tabelafeaturesmusicas = pd.read_sql_query(caracteristicasporpopularidade, conexao)
print(tabelafeaturesmusicas, '\n')


#identidade sonora de cada gênero
dnadosgeneros = """
SELECT tks.track_genre AS "genre", COUNT(*) AS tracks_quantity, -- selecionando o gênero, as médias das características musicais e a quantidade de músicas por gênero
ROUND(AVG(tdt.danceability), 2) AS "avg_danceability", ROUND(AVG(tdt.energy), 2) AS "avg_energy", ROUND(AVG(tdt.loudness), 2) AS "avg_loudness",
ROUND(AVG(tdt.speechiness), 2) AS "avg_speechiness", ROUND(AVG(tdt.acousticness), 2) AS "avg_acousticness", ROUND(AVG(tdt.liveness), 2) AS "avg_liveness",
ROUND(AVG(tdt.valence), 2) AS "avg_valence", ROUND(AVG(tdt.tempo), 2) AS "avg_tempo" 
FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id   -- relacionando as duas tabelas principais
GROUP BY genre ORDER BY (SUM(tdt.popularity >= 80) / COUNT(*)) DESC LIMIT 20;  -- selecionando os 20 gêneros com maior percentual de músicas populares
"""
tabeladnadosgeneros = pd.read_sql_query(dnadosgeneros, conexao)
print(tabeladnadosgeneros, '\n')


#visualizando as consultas
#paleta de cores dos gráficos
greens = [
    '#0B3D20',
    '#104A28',
    '#155730',
    '#1A6438',
    '#1F7140',
    '#247E48',
    '#298B50',
    '#2E9858',
    '#33A560',
    '#38B268',
    '#3DBF70',
    '#42CC78',
    '#47D980',
    '#4CE688',
    '#51ED8F',
    '#56F096',
    '#5BF29C',
    '#60F4A2',
    '#65F6A8',
    '#6AF8AE'
]

#PRIMEIRA CONSULTA
#criando o gráfico de ranking dos artistas e definindo as cores padronizadas
fig1 = px.bar(tabelaartistasmaispopulares, x=tabelaartistasmaispopulares['avg_popularity'], y=tabelaartistasmaispopulares['artist'], orientation='h', color='artist', color_discrete_sequence=greens)
fig1.update_layout(showlegend=False)

#definindo o tamanho do gráfico e ocultando a legenda
fig1.update_layout(
    width=800,  
    height=400, 
    showlegend=False
)

#personalizando o hover
fig1.update_traces(
   hovertemplate=
   'Popularidade média: %{x}<br>' +
   'Artista: %{y}<extra></extra>'
)


#SEGUNDA CONSULTA
#criando o gráfico de gêneros e definindo as cores padronizadas
fig2 = px.bar(tabelagenerosmaispopulares, x=tabelagenerosmaispopulares['tracks_quantity'], y=tabelagenerosmaispopulares['genre'], orientation='h', color='genre', color_discrete_sequence=greens, hover_data=['popular_percent'])
fig2.update_layout(
    width=800,  
    height=400, 
    showlegend=False
)

#personalizando o hover 
fig2.update_traces(
   hovertemplate=
   'Quantidade de músicas: %{x}<br>' + 
   'Gênero: %{y}<br>' +    
   'Percentual de músicas populares: %{customdata[0]}<extra></extra>'
)


#TERCEIRA CONSULTA
#criando o gráfico de artistas mais populares por gênero e definindo as cores padronizadas
fig3 = px.bar(tabelaartistasporgenero, x=tabelaartistasporgenero['avg_popularity'], y=tabelaartistasporgenero['genre'], orientation='h', color='genre', color_discrete_sequence=greens, hover_data=['artist'])
fig3.update_layout(
    width=800,  
    height=400, 
    showlegend=False
)

#personalizando o hover e os nomes exibidos
fig3.update_traces(
   hovertemplate=
   'Gênero: %{y}<br>' + 
   'Artista: %{customdata[0]}<br>' +
   'Popularidade média do artista: %{x}<extra></extra>'
)


#QUARTA CONSULTA
#definindo os limites mínimo e máximo de cada característica
limitesabsolutosfeatures = {
    'avg_danceability': (0, 1),
    'avg_energy': (0, 1),
    'avg_loudness': (-49.5, 4.5),
    'avg_speechiness': (0, 1),
    'avg_acousticness': (0, 1),
    'avg_liveness': (0, 1),
    'avg_valence': (0, 1),
    'avg_tempo': (0, 243),
    'avg_duration_ms': (0, 5200000)
}

#normalizando as características dos dois grupos para visualizar no gráfico
for caracteristica, (minimo,maximo) in limitesabsolutosfeatures.items():
    tabelafeaturesmusicas.loc[tabelafeaturesmusicas['feature'] == caracteristica, 'most_popular_normalized'] = (
        tabelafeaturesmusicas.loc[tabelafeaturesmusicas['feature'] == caracteristica, 'most_popular'] - minimo
        ) / (maximo - minimo)

#usando .loc porque as características estão organizadas em linhas devido ao UNION ALL
for caracteristica, (minimo,maximo) in limitesabsolutosfeatures.items():
    tabelafeaturesmusicas.loc[tabelafeaturesmusicas['feature'] == caracteristica, 'less_popular_normalized'] = (
        tabelafeaturesmusicas.loc[tabelafeaturesmusicas['feature'] == caracteristica, 'less_popular'] - minimo
        ) / (maximo - minimo)

fig4 = go.Figure() #criando o gráfico

fig4.add_trace(  #criando a visualização do grupo mais popular no gráfico
    go.Scatterpolar(
        r=tabelafeaturesmusicas['most_popular_normalized'],
        theta=tabelafeaturesmusicas['feature'],
        customdata=tabelafeaturesmusicas['most_popular'],
        fill='toself',
        name='20 músicas mais populares',
        line=dict(color='#36B569'),
        hovertemplate=
           'Característica: %{theta}<br>' +
           'Média não normalizada: %{customdata}<extra></extra>'
    )
)

fig4.add_trace(  #criando a visualização do grupo menos popular no gráfico
    go.Scatterpolar(
        r=tabelafeaturesmusicas['less_popular_normalized'],
        theta=tabelafeaturesmusicas['feature'],
        customdata=tabelafeaturesmusicas['less_popular'],
        fill='toself',
        name='20 músicas menos populares',
        line=dict(color='#006400'),
        hovertemplate=
            'Característica: %{theta}<br>' +
            'Média não normalizada: %{customdata}<extra></extra>'
    )
)

fig4.update_layout(  #personalizando as configurações visuais do gráfico
    polar=dict(
        radialaxis=dict(
            range=[0,1],
            visible=True
        )
    ),
    showlegend=False
)   


#exibindo os gráficos no streamlit
st.set_page_config(
    page_title='Spotify: além da música',   #configurando as informações da página
    page_icon='🎧',
    layout='wide'
)

col1, col2, col3, col4, col5 = st.columns([1, 0.5, 0.5, 0.5, 0.5])  #criando o título do projeto e exibindo as métricas da base de dados
col1.markdown(""" 
    <h1 style='text-align: left; margin-top: -60px; margin-bottom: 10px; font-size: 42px; font-weight: bold;'>
    Spotify: além da música
    </h1>
    """,
    unsafe_allow_html=True            
)

#criando as métricas dinâmicas da base de dados
totalmusicas = """
SELECT COUNT(*) AS count FROM tracks;
"""
tabelatotalmusicas = pd.read_sql_query(totalmusicas, conexao)
col2.metric('🎵 Total de músicas ', f'{tabelatotalmusicas["count"][0]:,}'.replace(',', '.'))


totalgeneros = """
SELECT COUNT(DISTINCT track_genre) AS count FROM tracks;
"""
tabelatotalgeneros = pd.read_sql_query(totalgeneros, conexao)
col3.metric('🎧 Total de gêneros ', f'{tabelatotalgeneros["count"][0]}')


tracks = pd.read_csv('data/tracks.csv', sep=',')  #contando cada artista de forma única (algumas tracks tem mais de um artista)
qtdartistas = (tracks['artists'].dropna().str.split(';').explode().str.strip().str.replace(r'\s+', ' ', regex=True).replace('', pd.NA).dropna().nunique())

col4.metric('🎤 Total de artistas ', f'{qtdartistas:,}'.replace(',', '.'))


mediapopularidade = """
SELECT ROUND((AVG(popularity)),1) AS popularity FROM tracksdetails;
"""
tabelamediapopularidade = pd.read_sql_query(mediapopularidade, conexao)
col5.metric('📊 Popularidade média ', f'{tabelamediapopularidade["popularity"][0]}')

st.markdown('---')


graf4, espaco1, graf5 = st.columns([4, 0.1, 4])  #criando o primeiro grupo de gráficos
with graf4:
    st.subheader('A Anatomia da Popularidade')
    st.write("""Comparando as características das 20 músicas mais populares
    com as 20 músicas menos populares.""")
    st.plotly_chart(fig4, width='stretch')

#QUINTA CONSULTA
with graf5:
    st.subheader('DNA Sonoro dos Gêneros')
    st.write("""A média das características sonoras de cada gênero.""")
    generoselecionado = st.selectbox('Gênero', (tabeladnadosgeneros['genre']))

    #normalizando loudness e tempo porque estão em escalas muito diferentes das demais características
    for feature in ['avg_loudness', 'avg_tempo']:
        tabeladnadosgeneros[f'{feature}_normalized'] = (
        (tabeladnadosgeneros[feature] - tabeladnadosgeneros[feature].min()) / 
        (tabeladnadosgeneros[feature].max() - tabeladnadosgeneros[feature].min())
        )

    listafeatures = [] 
    for feature in tabeladnadosgeneros: #selecionando as características que serão exibidas no gráfico
        if feature != 'genre' and feature != 'tracks_quantity' and feature != 'avg_tempo' and feature != 'avg_loudness':
            listafeatures.append(feature)

    mediasdogenero = tabeladnadosgeneros[tabeladnadosgeneros['genre'] == generoselecionado].iloc[0]

    if generoselecionado:
        fig5 = px.bar(x=mediasdogenero[listafeatures], y=listafeatures, orientation='h', color=listafeatures, color_discrete_sequence=greens)
        fig5.update_traces(
            hovertemplate='%{y}<br>Média: '
            '%{x:.2f}<extra></extra>'
            )
        fig5.update_layout(showlegend=False)
        fig5.update_layout(xaxis_title='valor médio')
        st.plotly_chart(fig5, width='stretch')


#criando o segundo grupo de gráficos
graf1, espaco1, graf2, espaco2, graf3 = st.columns([3, 0.1, 3, 0.1, 3])
with graf1:
    st.subheader('Artistas mais populares')
    st.write("""Os 12 artistas (com pelo menos 5 músicas) com as maiores médias de popularidade.""")
    st.plotly_chart(fig1, width='stretch')

with graf2:
    st.subheader('Gêneros mais populares')
    st.write("""Os 14 gêneros com maior percentual de músicas populares (popularidade >= 80).""")
    st.plotly_chart(fig2, width='stretch')

with graf3:
    st.subheader('Artistas mais populares por gênero')
    st.write("""Os 14 gêneros mais populares e seus artistas com as maiores médias de popularidade.""")
    st.plotly_chart(fig3, width='stretch')

conexao.dispose() #fechando a conexão

#importação das bibliotecas
import pyodbc
import pandas as pd 
import plotly.express as px

#conectando com o banco de dados do MySQL
conexao = pyodbc.connect(       
    "DRIVER={MySQL ODBC 26.7 Unicode Driver};"  
    "SERVER=localhost;"
    "DATABASE=spotifydatabase;"
    "UID=root;"
    "PWD=26022010jj;"
)

cursor = conexao.cursor() #abrindo o cursor

#ranking de artistas com no mínimo 5 músicas por maiores médias de popularidade
artistasmaispopulares = """ 
SELECT CASE WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ";") - 1)   -- selecionando apenas o artista principal da faixa
ELSE tks.artists
END AS "artist",  AVG(tdt.popularity) AS "avg_popularity"       -- selecionando a média de popularidade
FROM tracks AS tks INNER JOIN tracksdetails AS tdt        -- juntando as informações das duas tabelas
ON tks.track_id = tdt.track_id                     -- as colunas que se correspondem nas tabelas (primary key e foreign key)
GROUP BY CASE 
        WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ';') - 1)   -- selecionando novamente o primeiro artista pois o groupby é "executado" antes do select pelo sql 
        ELSE tks.artists
    END 
HAVING COUNT(tks.track_name) >= 5 ORDER BY avg_popularity DESC LIMIT 12;   -- limitando pra artistas com 5 musicas mínimas e ordenando por popularidade
"""
tabelaartistasmaispopulares = pd.read_sql_query(artistasmaispopulares, conexao) #criando uma tabela do pandas com os dados
#print(tabelaartistasmaispopulares)



#generos mais populares
generosmaispopulares = """
SELECT tks.track_genre AS "genre", COUNT(*) AS "tracks_quantity", 
CONCAT(ROUND((SUM(tdt.popularity >= 80) / COUNT(*) * 100), 2), "%") AS "popular_percent"  -- selecionando as colunas de genero e criando as colunas de percentual de musicas populares e quantidade de musicas 
FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id   -- juntando as duas tabelas
GROUP BY genre ORDER BY popular_percent DESC LIMIT 17;  -- cada genero aparecendo uma única vez

"""
tabelagenerosmaispopulares = pd.read_sql_query(generosmaispopulares, conexao)
#print(tabelagenerosmaispopulares)



#artistas mais populares de cada genero
artistasporgenero = """
WITH top_genres AS (   -- criando a cte que armazena os generos mais populares (que aparecem na ultima consulta)
    SELECT tks.track_genre AS "genre"
    FROM tracks AS tks INNER JOIN tracksdetails AS tdt   
    ON tks.track_id = tdt.track_id
    GROUP BY genre
    ORDER BY (SUM(tdt.popularity >= 80) / COUNT(*)) DESC LIMIT 12
),

artist_avg AS (
    SELECT tks.track_genre AS genre, CASE WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ";") - 1)   -- selecionando apenas o artista principal da faixa
	ELSE tks.artists  -- selecionando o principal artista de cada track
    END AS "artist", 
    ROUND(AVG(tdt.popularity), 2) AS avg_popularity -- criando a média de popularidade
    FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id
    INNER JOIN top_genres AS tg ON tks.track_genre = tg.genre  -- juntando as duas tabelas principais com a cte dos generos mais populares
    GROUP BY genre, artist
),

ranked_artists AS (
    SELECT artist, genre, avg_popularity, 
    ROW_NUMBER() OVER -- window function para agrupar os generos e selecionar o artista mais popular de cada genero
    (PARTITION BY genre ORDER BY avg_popularity DESC) AS ranking 
    FROM artist_avg
)

SELECT
    genre, CASE WHEN INSTR(ranked_artists.artist, ';') > 0 THEN LEFT(ranked_artists.artist, INSTR(ranked_artists.artist, ";") - 1)   -- selecionando apenas o artista principal da faixa
		   ELSE ranked_artists.artist  -- selecionando apenas o artista principal da faixa
		   END AS "artist",
	avg_popularity
    FROM ranked_artists
    WHERE ranking = 1 -- selecionando o artista com maior popularidade em cada genêro
	ORDER BY avg_popularity DESC;

"""
tabelaartistasporgenero = pd.read_sql_query(artistasporgenero, conexao)
#print(tabelaartistasporgenero)



#caracteristas das musicas mais populares vs das musicas menos populares
caracteristicasporpopularidade = """
WITH toppopular AS ( SELECT *
FROM tracksdetails              -- cte contendo as 20 musicas mais populares
ORDER BY popularity DESC
LIMIT 20
),
bottompopular AS (SELECT *
FROM tracksdetails              -- cte contendo as 20 musicas menos populares
ORDER BY popularity ASC
LIMIT 20
)

-- selecionando as médias de cada caracteristica das musicas e separando pelas mais populares e menos populares
SELECT "avg_duration_ms" AS feature,
ROUND((SELECT AVG(duration_ms) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(duration_ms) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(duration_ms) FROM toppopular) - (SELECT AVG(duration_ms) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(duration_ms) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL  -- empilhando os selects de cada caracteristica em linhas

SELECT "avg_danceability",
ROUND((SELECT AVG(danceability) FROM toppopular), 2), 
ROUND((SELECT AVG(danceability) FROM bottompopular), 2),
CONCAT(
    ROUND((((SELECT AVG(danceability) FROM toppopular) - (SELECT AVG(danceability) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(danceability) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL

SELECT "avg_energy",
ROUND((SELECT AVG(energy) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(energy) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(energy) FROM toppopular) - (SELECT AVG(energy) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(energy) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL

SELECT "avg_loudness",
ROUND((SELECT AVG(loudness) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(loudness) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(loudness) FROM toppopular) - (SELECT AVG(loudness) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(loudness) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL

SELECT "avg_speechiness",
ROUND((SELECT AVG(speechiness) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(speechiness) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(speechiness) FROM toppopular) - (SELECT AVG(speechiness) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(speechiness) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL

SELECT "avg_acousticness",
ROUND((SELECT AVG(acousticness) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(acousticness) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(acousticness) FROM toppopular) - (SELECT AVG(acousticness) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(acousticness) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL

SELECT "avg_valence",
ROUND((SELECT AVG(valence) FROM toppopular), 2) AS most_popular, 
ROUND((SELECT AVG(valence) FROM bottompopular), 2) AS less_popular,
CONCAT(
    ROUND((((SELECT AVG(valence) FROM toppopular) - (SELECT AVG(valence) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(valence) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 
UNION ALL

SELECT "avg_tempo",
ROUND((SELECT AVG(tempo) FROM toppopular), 2), 
ROUND((SELECT AVG(tempo) FROM bottompopular), 2),
CONCAT(
    ROUND((((SELECT AVG(tempo) FROM toppopular) - (SELECT AVG(tempo) FROM bottompopular)) 
		  / NULLIF((SELECT AVG(tempo) FROM bottompopular), 0)) * 100, 2 ),'%') AS "percent_difference" 

"""
tabelamusicaspopulares = pd.read_sql_query(caracteristicasporpopularidade, conexao)
#print(tabelamusicaspopulares)



#identidade sonoro de cada genero
dnadosgeneros = """
SELECT tks.track_genre AS "genre", COUNT(*) AS tracks_quantity, -- selecionando as colunas de genero, médias das caracteristicas musicais e quantidade de musicas por genero
ROUND(AVG(tdt.danceability), 2) AS "avg_danceability", ROUND(AVG(tdt.energy), 2) AS "avg_energy", ROUND(AVG(tdt.loudness), 2) AS "avg_loudness",
ROUND(AVG(tdt.speechiness), 2) AS "avg_speechiness", ROUND(AVG(tdt.acousticness), 2) AS "avg_acousticness", ROUND(AVG(tdt.liveness), 2) AS "avg_liveness",
ROUND(AVG(tdt.valence), 2) AS "avg_valence", ROUND(AVG(tdt.tempo), 2) AS "avg_tempo" 
FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id   -- juntando as duas tabelas principais
GROUP BY genre ORDER BY (SUM(tdt.popularity >= 80) / COUNT(*)) DESC LIMIT 20;  -- selecionando os 20 generos com maior quantidade de musicas populares
"""

tabeladnadosgeneros = pd.read_sql_query(dnadosgeneros, conexao)
#print(tabeladnadosgeneros)

cursor.close() #fechando o cursor
conexao.close() #fechando a conexão



#visualizando as consultas

#paleta de cores dos gráficos
greens = [
    "#0B3D20",
    "#104A28",
    "#155730",
    "#1A6438",
    "#1F7140",
    "#247E48",
    "#298B50",
    "#2E9858",
    "#33A560",
    "#38B268",
    "#3DBF70",
    "#42CC78",
    "#47D980",
    "#4CE688",
    "#51ED8F",
    "#56F096",
    "#5BF29C",
    "#60F4A2",
    "#65F6A8",
    "#6AF8AE"
]

#PRIMEIRACONSULTA

#criando o gráfico com as informações da sua respectiva tabela e selecionando o hover e as cores padronizadas
#fig = px.bar(tabelaartistasmaispopulares, x=tabelaartistasmaispopulares["artist"], y=tabelaartistasmaispopulares["avg_popularity"], color=artist, color_discrete_sequence=greens)
#fig.update_layout(showlegend=False)

#excluindo a linha de color do hover e personalizando os nomes das legendas (nomes das colunas) 
#fig.update_traces(
 #   hovertemplate=
  #  "Artista: %{x}<br>" +
   # "Popularidade Média: %{y}<extra></extra>"
#)

#fig.show()



#SEGUNDA CONSULTA 

#criando o gráfico com as informações da sua respectiva tabela e selecionando o hover e as cores padronizadas
fig = px.bar(tabelagenerosmaispopulares, x=tabelagenerosmaispopulares["genre"], y=tabelagenerosmaispopulares["tracks_quantity"], color="genre", color_discrete_sequence=greens, hover_data=["popular_percent"])
fig.update_layout(showlegend=False)

#excluindo a linha de color do hover e personalizando os nomes das legendas (nomes das colunas) 
fig.update_traces(
    hovertemplate=
    "Gênero: %{x}<br>" + 
    "Quantidade de músicas: %{y}<br>" +    
    "Percentual de musicas populares: %{customdata[0]}<extra></extra>"
)

fig.show()



#TERCEIRA CONSULTA 
#criando o gráfico com as informações da sua respectiva tabela e selecionando o hover e as cores padronizadas
fig = px.bar(tabelaartistasporgenero, x=tabelaartistasporgenero["avg_popularity"], y=tabelaartistasporgenero["genre"], orientation='h', color="genre", color_discrete_sequence=greens, hover_data=["artist"])
fig.update_layout(showlegend=False)

#começando das barras maiores para as menores
fig.update_yaxes(categoryorder="total ascending")

#excluindo a linha de color do hover e personalizando os nomes das legendas (nomes das colunas) 
fig.update_traces(
    hovertemplate=
    "Gênero: %{y}<br>" + 
    "Artista: %{customdata[0]}<br>" +
    "Popularidade média do artista: %{x}<extra></extra>"
)
fig.show()




#QUARTA CONSULTA 
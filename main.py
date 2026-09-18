#importação das bibliotecas
import pyodbc
import pandas as pd 


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
END AS "artists",  AVG(tdt.popularity) AS "popularity"       -- selecionando a média de popularidade
FROM tracks AS tks INNER JOIN tracksdetails AS tdt        -- juntando as informações das duas tabelas
ON tks.track_id = tdt.track_id                     -- as colunas que se correspondem nas tabelas (primary key e foreign key)
GROUP BY CASE 
        WHEN INSTR(tks.artists, ';') > 0 THEN LEFT(tks.artists, INSTR(tks.artists, ';') - 1)   -- selecionando novamente o primeiro artista pois o groupby é "executado" antes do select pelo sql 
        ELSE tks.artists
    END 
HAVING COUNT(tks.track_name) >= 5 ORDER BY popularity DESC LIMIT 20;   -- limitando pra artistas com 5 musicas mínimas e ordenando por popularidade
"""

#dados = cursor.fetchall() #armazenando os dados da consulta em uma variavel
tabelaartistasmaispopulares = pd.read_sql_query(artistasmaispopulares, conexao) #criando uma tabela do pandas com os dados
print(tabelaartistasmaispopulares)



#generos mais populares
generosmaispopulares = """
                SELECT tks.track_genre AS "genre", COUNT(*) AS "tracks_quantity", 
CONCAT(ROUND((SUM(tdt.popularity >= 80) / COUNT(*) * 100), 2), "%") AS "popular_percent"  -- selecionando as colunas de genero e criando as colunas de percentual de musicas populares e quantidade de musicas 
FROM tracks AS tks INNER JOIN tracksdetails AS tdt ON tks.track_id = tdt.track_id   -- juntando as duas tabelas
GROUP BY genre ORDER BY popular_percent DESC LIMIT 20;  -- cada genero aparecendo uma única vez

"""

tabelagenerosmaispopulares = pd.read_sql_query(generosmaispopulares, conexao)
print(tabelagenerosmaispopulares)


#artistas mais populares com x musicas minimas  CHECKS

#generos mais populares
#artistas mais populares de cada genero
#artistas mais versateis 
#identidade sonora de cada genero
#caracteristas das musicas mais populares vs das musicas menos populares
#caracteristicas das musicas mais DANÇANTES
#musicas mais populares de cada genero

cursor.close() #fechando o cursor
conexao.close() #fechando a conexão
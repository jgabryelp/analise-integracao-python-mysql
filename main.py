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
cursor.execute(""" 
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
""")

dados = cursor.fetchall() #armazenando os dados da consulta em uma variavel
tabeladados = pd.DataFrame(dados) #criando uma tabela do pandas com os dados
print(tabeladados)



#artistas mais populares de cada genero
cursor.execute("""
                SELECT * FROM tracks LIMIT 10

""")

dados = cursor.fetchall()
tabeladados = pd.DataFrame(dados)
print(tabeladados)


#artistas mais populares com x musicas minimas  CHECKS

#artistas mais populares de cada genero
#artistas mais versateis 
#generos mais populares
#identidade sonora de cada genero
#caracteristas das musicas mais populares vs das musicas menos populares
#caracteristicas das musicas mais DANÇANTES
#musicas mais populares de cada genero

cursor.close() #fechando o cursor
conexao.close() #fechando a conexão
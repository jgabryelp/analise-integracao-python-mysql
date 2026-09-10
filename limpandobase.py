import pandas as pd

basededados = pd.read_csv("spotify-tracks-dataset-detailed.csv", sep = ",") #importando a base de dados bruta

tracks = basededados[["track_id", "track_name", "artists", "album_name", "track_genre", "explicit"]]  #selecionando as colunas da tabela "tracks"
tracksdetails = basededados[["track_id","popularity", "duration_ms", "danceability", "energy", "loudness", "speechiness", "acousticness", "liveness", "valence", "tempo"]] #selecionando as colunas da tabela tracksdetails


import unicodedata #importando a biblioteca unicode, pra trabalhar com carecteres especiais

def limpar_texto(texto):
    if isinstance(texto, str):
        return unicodedata.normalize("NFKD", texto).encode(  #funçao que exclui caracteres especiais como as letras japonesas
            "ascii", "ignore"
        ).decode("ascii")
    return texto

for coluna in tracks.select_dtypes(include="str").columns:
    tracks[coluna] = tracks[coluna].apply(limpar_texto) #aplicando a função que limpa os caracteres na tabela tracks

for coluna in tracksdetails.select_dtypes(include="str").columns:
    tracksdetails[coluna] = tracksdetails[coluna].apply(limpar_texto) #aplicando a função que limpa os caracteres na tabela tracksdetails


tracks.to_csv("tracks.csv", sep=',', encoding='utf-8', index=False) #exportando as tabelas em csv pra abrir no mysql
tracksdetails.to_csv("tracksdetails.csv", sep=',', encoding='utf-8', index=False)

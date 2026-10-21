# Spotify: Beyond Music 🎶
## O que é o projeto:
Um dashboard interativo feito utilizando Python com diversas análises de padrões e tendências de uma base de dados com mais de 100 mil músicas do Spotify. As análises são feitas por consultas SQL conectadas a um banco de dados MySQL hospedado em um servidor da Aiven. Além disso o dashboard está disponível em uma aplicação web desenvolvida com Streamlit. Acesso ao [dashboard](https://spotifygobeyond.streamlit.app).

## 📁 Base de dados original do projeto: 
[Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data)

## 🧹 Tratamento da base de dados:
A base de dados original continha alguns caracteres em japonês que estavam conflitando com o MySQL, como solução eu decidi limpar a base de dados excluindo qualquer linha que tivesse caracteres japoneses em qualquer uma de suas colunas, usando esse código: [limpandobase.py](https://github.com/jgabryelp/analise-integracao-python-mysql/blob/main/data/limpandobase.py)

## 📈 Análises realizadas:
* O que faz uma música ser popular?
* A identidade sonora dos gêneros mais famosos
* Os artistas com maiores médias de popularidade
* Os gêneros com maiores médias de popularidade
* Os artistas mais populares de cada gênero

## 📊 O dashboard:
[streamlit-main-2026-10-19-17-12-14.webm](https://github.com/user-attachments/assets/961e4684-f35e-4a82-8b49-70d9cfdc3320)


## 🛠️ Tecnologias utilizadas:
* Python 
* Pandas
* Plotly
* Streamlit
* SQL
* SQLAlchemy
* MySQL

## 🚀 Como executar:
1 - Tenha baixado em seu sistema as bibliotecas contidas no arquivo [requirements.txt](https://github.com/jgabryelp/analise-integracao-python-mysql/blob/main/requirements.txt). 
<br/>
2 - Estabeleça uma conexão com um servidor MySQL contendo as tabelas tratadas armazenadas na pasta [data](https://github.com/jgabryelp/analise-integracao-python-mysql/tree/main/data)
<br/>
3 - Modifique o valor das variáveis de conexão do código [main.py](https://github.com/jgabryelp/analise-integracao-python-mysql/blob/main/main.py) para os valores correspondentes ao seu nome de usuário, nome do banco de dados, servidor local, port, e senha de usuário. E certifique-se de disponibilizar o certificado CA no arquivo [ca.pem](https://github.com/jgabryelp/analise-integracao-python-mysql/blob/main/config/ca.pem)
<br/>
4 - Rode o código e no terminal rode o comando: "streamlit run main.py" pra iniciar o dashboard.

## 📝 Autor:
João Gabryel Caldeira: 
<br/>
Email - joaogabryelcaldeirap@gmail.com
<br/>
LinkedIn - [João Gabryel](https://www.linkedin.com/in/jo%C3%A3o-gabryelc/)
<br/>

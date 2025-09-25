# Importando as bibliotecas
import sqlite3
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Estabelecendo ou criando banco de dados, caso não exista
con = sqlite3.connect("status_saldo.db")

#Criando variavel cursor e criando a tabela, caso não exista
cursor = con.cursor()
cursor.execute("""
 CREATE TABLE IF NOT EXISTS status_saldo (
    id_status_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_funcionario TEXT NOT NULL UNIQUE,  
    saldo_total_mes REAL NOT NULL,             
    saldo_usado_agosto REAL,
    saldo_usado_setembro REAL,
    saldo_usado_outubro REAL,                                            
    saldo_usado_total REAL
);
""")

#Criando conexão com os outros banco de dados via SQL
cursor.execute("ATTACH DATABASE 'banco_funcionarios\\banco_funcionarios.db' AS banco_funcionarios")
cursor.execute("ATTACH DATABASE 'banco_vendas\\banco_vendas.db' AS banco_vendas")

#Criando dataframes dos databases importados, também via SQL
df_funcionarios = pd.read_sql("SELECT * FROM banco_funcionarios.funcionario AS funcionarios", con)
df_vendas = pd.read_sql("SELECT * FROM banco_vendas.venda AS VENDAS", con)

#Removendo linhas duplicadas da tabela de vendas
#(Como a tabela possui id unico precisamos inserir os parametros, colunas, de comparação)
df_vendas.drop_duplicates(subset=['nome_registro', 'nome_livro', 'valor', 'data_venda'], keep='first', inplace=True)

#Fazendo soma condiocional: somar pelo nome e dentro de um mês em especifico
    #Altera dataframe de vendas deixando apenas os registros de venda, cujo o nome registrado está dentro da tabela de funcionários
df_vendas = df_vendas[df_vendas['nome_registro'].isin(df_funcionarios['nome'])]

    #Cria variavel que pega apenas os dados da data de venda e indica que os dados são datas
datas = pd.to_datetime(df_vendas['data_venda'])

    #Cria dataframes para cada mês, utilizando o comando loc para aplicar critérios de datas nos mesmos
df_agosto = df_vendas.loc[(datas >= dt.datetime(2025, 8, 1)) & (datas <= dt.datetime(2025, 8, 30))]
df_setembro = df_vendas.loc[(datas >= dt.datetime(2025, 9, 1)) & (datas <= dt.datetime(2025, 9, 30))]
df_outubro = df_vendas.loc[(datas >= dt.datetime(2025, 10, 1)) & (datas <= dt.datetime(2025, 10, 30))]

    #Cria dataframes que fazem a soma das informormações de valor agrupando pelo nome
    #Utiliza comando reset_index() para converter resultados em formato de colunas
df_saldo_agosto = df_agosto.groupby('nome_registro')['valor'].sum().reset_index()
df_saldo_setembro = df_setembro.groupby('nome_registro')['valor'].sum().reset_index()
df_saldo_outubro = df_outubro.groupby('nome_registro')['valor'].sum().reset_index()
df_saldo_total = df_vendas.groupby('nome_registro')['valor'].sum().reset_index()

#Utiliza comando zip para compactar, dentro de uma variavél, informações especificas de valores de diferetes dataframes
dados = list(zip(
    df_funcionarios['nome'],
    df_funcionarios['saldo_total'],
    df_saldo_agosto['valor'],
    df_saldo_setembro['valor'],
    df_saldo_outubro['valor'],
    df_saldo_total['valor']
))

#Insere os dados compactados dentro da tabela de status_saldo
cursor.executemany("""
INSERT OR IGNORE INTO status_saldo (nome_funcionario, saldo_total_mes, saldo_usado_agosto, saldo_usado_setembro,
                   saldo_usado_outubro, saldo_usado_total)
VALUES (?, ?, ?, ?, ?, ?)         
""", dados)

#Cria dataframe da tabela 'status_saldo', via SQL
df_status_saldo = pd.read_sql("SELECT * FROM status_saldo AS status_saldo", con)

print(df_status_saldo)

#Estiliza graficos a serem plotados
sns.set_theme(style="whitegrid", palette="pastel", font="sans-serif", context="notebook")

#Utiliza de subplots para plotar quatro graficos em apenas uma linha
fig, axes = plt.subplots(1, 4, figsize=(15,5))

#Plota graficos de saldo gasto para cada mês e de todos os meses, por funcionario
sns.barplot(x='nome_funcionario', y='saldo_usado_agosto', data=df_status_saldo, ax=axes[0])
axes[0].set_title("Saldo gasto de agosto")
sns.barplot(x='nome_funcionario', y='saldo_usado_setembro', data=df_status_saldo, ax=axes[1])
axes[1].set_title("Saldo gasto de setembro")
sns.barplot(x='nome_funcionario', y='saldo_usado_outubro', data=df_status_saldo, ax=axes[2])
axes[2].set_title("Saldo gasto de outubro")
sns.barplot(x='nome_funcionario', y='saldo_usado_total', data=df_status_saldo, ax=axes[3])
axes[3].set_title("Saldo gasto de outubro - setembro")

#Plota grafico comparando os saldos totais gasto dentro de cada mês
valores = (sum(df_status_saldo['saldo_usado_agosto']), sum(df_status_saldo['saldo_usado_setembro']), sum(df_status_saldo['saldo_usado_outubro']))
totais_saldo_usado = [round(v,2) for v in valores]
messes = ("agosto", "setembro", "outubro")
plt.figure(figsize=(6,6)) 
comparativo_mes = sns.lineplot(x=messes, y=totais_saldo_usado, data=df_status_saldo, marker='o')
comparativo_mes.set_title("Comparativos agosto - setembro")

#Adicona rotulos nos eixos x e y em todos os gráficos
comparativo_mes.set_xlabel("Meses")
comparativo_mes.set_ylabel("Valor")
axes = (axes[0], axes[1], axes[2], axes[3])
for ax in axes:
    ax.set_xlabel("Funcionários")
    ax.set_ylabel("Valor")

#Adiciona os valores de valor em cada um dos gráficos
for i, valor in enumerate(df_status_saldo['saldo_usado_agosto']):
    axes[0].text(i, valor + 0.1, f"R$ {valor}", ha='center', va='bottom')
for i, valor in enumerate(df_status_saldo['saldo_usado_setembro']):
    axes[1].text(i, valor + 0.1, f"R$ {valor}", ha='center', va='bottom')
for i, valor in enumerate(df_status_saldo['saldo_usado_outubro']):
    axes[2].text(i, valor + 0.1, f"R$ {valor}", ha='center', va='bottom')
for i, valor in enumerate(df_status_saldo['saldo_usado_total']):
    axes[3].text(i, valor + 0.1, f"R$ {valor}", ha='center', va='bottom')
for i, valor in enumerate(totais_saldo_usado):
    comparativo_mes.text(i, valor + 0.1, f"R$ {valor}", ha='left', va='bottom')

#Exprota os dados da tabela 'status_saldo' para exel e os graficos em imagens
df_status_saldo.to_excel("status_saldo.xlsx", index=False)
fig.savefig("Graficos.png", dpi=300)
plt.savefig("Grafico_comparativo.png", dpi=300)

con.commit()
con.close()
plt.tight_layout()
plt.show()
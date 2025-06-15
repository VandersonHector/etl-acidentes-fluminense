import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Configurações do banco de dados
db_config = {
    'user': 'postgres',  
    'password': 'passWord11', 
    'host': 'localhost',
    'port': '5432',
    'database': 'acidentes_fluminense_db'
}

# Extração
def extract_data(file_path):
    print("Extraindo dados...")
    df = pd.read_csv(file_path, encoding='latin1', delimiter=';', low_memory=False)
    return df

df = extract_data(r"C:\Users\vande\Documents\DS Arquivos\etl-acidentes-fluminense\Data\demostrativo_acidentes_af.csv")

# Passo 2: Transformação
def transform_data(df):
    print("Transformando dados...")
# Renomear colunas para padronizar (ajuste conforme o CSV)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ã', 'a').str.replace('ç', 'c')

    expected_columns = [
        'data', 'horario', 'n_da_ocorrencia', 'tipo_de_ocorrencia', 'km',
        'trecho', 'sentido', 'tipo_de_acidente', 'automovel', 'bicicleta',
        'caminhao', 'moto', 'onibus', 'outros', 'tracao_animal',
        'transporte_de_cargas_especiais', 'trator_maquinas', 'utilitarios',
        'ilesos', 'levemente_feridos', 'moderadamente_feridos',
        'gravemente_feridos', 'mortos'
    ]
    if not all(col in df.columns for col in expected_columns):
        missing = [col for col in expected_columns if col not in df.columns]
        raise ValueError(f"Colunas faltando: {missing}")
    
    # Renomear colunas para corresponder à tabela
    df = df.rename(columns={'data': 'data_acidente'})

    # Tratar valores nulos
    df['tipo_de_ocorrencia'] = df['tipo_de_ocorrencia'].fillna('Desconhecido')
    df['tipo_de_acidente'] = df['tipo_de_acidente'].fillna('Desconhecido')
    df['trecho'] = df['trecho'].fillna('Não informado')
    df['sentido'] = df['sentido'].fillna('Não informado')

    # Converter data para formato correto
    df['data_acidente'] = pd.to_datetime(df['data_acidente'], format='%d/%m/%Y', errors='coerce')

    # Converter horário para TIME
    df['horario'] = pd.to_datetime(df['horario'], format='%H:%M:%S', errors='coerce').dt.time
    
    # Converter km para float
    df['km'] = pd.to_numeric(df['km'], errors='coerce').fillna(0.0)
    
    # Converter colunas numéricas
    numeric_columns = [
        'automovel', 'bicicleta', 'caminhao', 'moto', 'onibus', 'outros',
        'tracao_animal', 'transporte_de_cargas_especiais', 'trator_maquinas',
        'utilitarios', 'ilesos', 'levemente_feridos', 'moderadamente_feridos',
        'gravemente_feridos', 'mortos'
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    # Remover duplicatas com base em n_da_ocorrencia
    df = df.drop_duplicates(subset=['n_da_ocorrencia'])
    
    return df

# Passo 3: Carga
def load_data(df, table_name):
    print("Carregando dados...")
    engine = create_engine(f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Dados carregados na tabela {table_name}")


# Passo 4: Visualização
def visualize_data(df):
    print("Gerando visualização...")
    acidentes_por_tipo = df.groupby('tipo_de_acidente').size().sort_values(ascending=False).head(5)
    
    plt.figure(figsize=(10, 6))
    acidentes_por_tipo.plot(kind='bar')
    plt.title('Top 5 Tipos de Acidentes na Autopista Fluminense')
    plt.xlabel('Tipo de Acidente')
    plt.ylabel('Número de Ocorrências')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('acidentes_por_tipo.png')
    plt.close()

# Passo 5: Visualização - Quantidade de acidentes por ano
def visualize_acidentes_por_ano(df):
    print("Gerando visualização de acidentes por ano...")
    # Extrair o ano da coluna data_acidente
    df['ano'] = df['data_acidente'].dt.year
    # Contar acidentes por ano
    acidentes_por_ano = df.groupby('ano').size()
    
    plt.figure(figsize=(10, 6))
    acidentes_por_ano.plot(kind='bar')
    plt.title('Quantidade de Acidentes por Ano na Autopista Fluminense (2010-2019)')
    plt.xlabel('Ano')
    plt.ylabel('Número de Acidentes')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('acidentes_por_ano.png')
    plt.close()

def main():
    file_path = r'C:\Users\vande\Documents\DS Arquivos\etl-acidentes-fluminense\Data\demostrativo_acidentes_af.csv'

    df = extract_data(file_path)
    df_transformed = transform_data(df)
    load_data(df_transformed, 'acidentes_fluminense')
    visualize_data(df_transformed)

if __name__ == '__main__':
    main()
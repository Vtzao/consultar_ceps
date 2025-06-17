import pandas as pd
import requests
import time

# --- CONFIGURAÇÕES ---
# Nome do arquivo de entrada e da coluna que contém os CEPs
ARQUIVO_ENTRADA = '2000ceps.xlsx'
COLUNA_DOS_CEPS = 'CEPS'

# Nome do arquivo que será criado com os resultados
ARQUIVO_SAIDA = 'enderecos_resultados.xlsx'
# ---------------------

def consultar_viacep(cep):
    """Consulta um único CEP na API do ViaCEP e retorna os dados em JSON."""
    try:
        # Limpa o CEP, deixando apenas números
        cep_limpo = ''.join(filter(str.isdigit, str(cep)))

        if len(cep_limpo) != 8:
            return {"Status": "Formato de CEP inválido"}

        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            dados_json = response.json()
            if "erro" in dados_json:
                return {"Status": "CEP não encontrado"}
            else:
                # Retorna o dicionário completo do endereço se for bem-sucedido
                return dados_json
        else:
            return {"Status": f"Erro na requisição (Código {response.status_code})"}

    except requests.exceptions.RequestException as e:
        return {"Status": f"Erro de Conexão: {e}"}

# --- INÍCIO DO SCRIPT PRINCIPAL ---

# 1. Ler o arquivo Excel
try:
    print(f"Lendo o arquivo de entrada: '{ARQUIVO_ENTRADA}'...")
    df = pd.read_excel(ARQUIVO_ENTRADA)
    print("Arquivo lido com sucesso.")
except FileNotFoundError:
    print(f"ERRO: Arquivo '{ARQUIVO_ENTRADA}' não encontrado. Verifique o nome e o local do arquivo.")
    exit()
except Exception as e:
    print(f"Ocorreu um erro ao ler a planilha: {e}")
    exit()

# Verifica se a coluna de CEPs existe
if COLUNA_DOS_CEPS not in df.columns:
    print(f"ERRO: A coluna '{COLUNA_DOS_CEPS}' não foi encontrada na planilha. Verifique o cabeçalho.")
    exit()

# 2. Lista para armazenar os resultados
lista_de_resultados = []

print(f"\nIniciando a consulta para {len(df)} CEPs. Isso pode levar um tempo...")

# 3. Loop para consultar cada CEP da planilha
for index, row in df.iterrows():
    cep_original = row[COLUNA_DOS_CEPS]

    print(f"Processando linha {index + 1}/{len(df)} - CEP: {cep_original}")

    # Consulta a API
    resultado_da_consulta = consultar_viacep(cep_original)

    # Prepara a linha para o novo arquivo Excel
    linha_nova = {
        'CEP_Consultado': cep_original,
        'Logradouro': resultado_da_consulta.get('logradouro', ''),
        'Bairro': resultado_da_consulta.get('bairro', ''),
        'Cidade': resultado_da_consulta.get('localidade', ''),
        'UF': resultado_da_consulta.get('uf', ''),
        'Status': resultado_da_consulta.get('Status', 'Sucesso') # Pega o status de erro ou define como Sucesso
    }
    lista_de_resultados.append(linha_nova)

    # Pausa para não sobrecarregar a API
    time.sleep(0.05)

# 4. Criar um novo DataFrame com os resultados
df_resultados = pd.DataFrame(lista_de_resultados)

# 5. Salvar o novo DataFrame em um arquivo Excel
try:
    print(f"\nSalvando os resultados no arquivo: '{ARQUIVO_SAIDA}'...")
    df_resultados.to_excel(ARQUIVO_SAIDA, index=False)
    print("Processo concluído com sucesso!")
except Exception as e:
    print(f"Ocorreu um erro ao salvar o arquivo de resultados: {e}")

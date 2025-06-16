import pandas as pd
import requests
import time

# --- CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = 'ceps.xlsx'
ARQUIVO_SAIDA = 'enderecos_completos.xlsx'
NOME_COLUNA_CEP = 'CEP'
# ---------------------

def consultar_cep(cep):
    """Consulta um único CEP na API do ViaCEP."""
    try:
        # Limpa o CEP, deixando apenas números
        cep_limpo = str(cep).strip().replace('.', '').replace('-', '')
        
        if len(cep_limpo) != 8 or not cep_limpo.isdigit():
            return {"erro": "Formato de CEP inválido"}

        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        response = requests.get(url, timeout=5) # Timeout de 5 segundos
        response.raise_for_status()  # Lança um erro para respostas ruins (4xx ou 5xx)
        
        data = response.json()
        return data

    except requests.Timeout:
        return {"erro": "Tempo de requisição excedido"}
    except requests.RequestException as e:
        return {"erro": f"Erro na requisição: {e}"}
    except Exception as e:
        return {"erro": f"Erro inesperado: {e}"}

def processar_planilha():
    """Lê a planilha, consulta os CEPs e salva o resultado."""
    try:
        df = pd.read_excel(ARQUIVO_ENTRADA)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{ARQUIVO_ENTRADA}' não encontrado. Verifique o nome e o local do arquivo.")
        return
    except Exception as e:
        print(f"ERRO ao ler a planilha: {e}")
        return

    if NOME_COLUNA_CEP not in df.columns:
        print(f"ERRO: A coluna '{NOME_COLUNA_CEP}' não foi encontrada na planilha.")
        return

    total_ceps = len(df)
    print(f"Iniciando a consulta de {total_ceps} CEPs...")

    resultados = []
    for index, row in df.iterrows():
        cep_original = row[NOME_COLUNA_CEP]
        
        # Consulta o CEP e trata o resultado
        endereco = consultar_cep(cep_original)
        
        # Adiciona os dados do endereço ao dicionário da linha original
        linha_resultado = row.to_dict()
        if not endereco.get('erro'):
            linha_resultado['Logradouro'] = endereco.get('logradouro', '')
            linha_resultado['Bairro'] = endereco.get('bairro', '')
            linha_resultado['Cidade'] = endereco.get('localidade', '')
            linha_resultado['UF'] = endereco.get('uf', '')
            linha_resultado['Status'] = 'Sucesso'
        else:
            # Mantém as colunas vazias e adiciona o status de erro
            linha_resultado['Logradouro'] = ''
            linha_resultado['Bairro'] = ''
            linha_resultado['Cidade'] = ''
            linha_resultado['UF'] = ''
            linha_resultado['Status'] = endereco.get('erro')

        resultados.append(linha_resultado)
        
        # Mostra o progresso no terminal
        print(f"Processando {index + 1}/{total_ceps} - CEP: {cep_original}")
        
        # Pequena pausa para não sobrecarregar a API
        time.sleep(0.05) 

    # Cria um novo DataFrame com os resultados
    df_resultado = pd.DataFrame(resultados)
    
    # Salva o novo DataFrame em um arquivo Excel
    try:
        df_resultado.to_excel(ARQUIVO_SAIDA, index=False)
        print(f"\nProcesso concluído! Os dados foram salvos no arquivo '{ARQUIVO_SAIDA}'.")
    except Exception as e:
        print(f"ERRO ao salvar o arquivo de saída: {e}")


# --- Inicia a execução do script ---
if __name__ == "__main__":
    processar_planilha()
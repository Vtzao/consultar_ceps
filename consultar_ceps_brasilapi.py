import pandas as pd
import requests
import time
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = 'ceps.xlsx'
ARQUIVO_SAIDA = 'enderecos_completos_brasilapi.xlsx' # Alterado para não sobrescrever o arquivo antigo
NOME_COLUNA_CEP = 'CEP'
LOTE_SALVAMENTO = 100
# ---------------------

def consultar_cep_brasilapi(cep):
    """Consulta um único CEP na BrasilAPI."""
    try:
        # A BrasilAPI não precisa de limpeza de caracteres, mas mantemos por segurança
        cep_limpo = ''.join(filter(str.isdigit, str(cep)))
        
        if len(cep_limpo) != 8:
            return {"erro": "Formato de CEP inválido"}

        # <<< MUDANÇA PRINCIPAL: URL DA BRASILAPI >>>
        url = f"https://brasilapi.com.br/api/cep/v1/{cep_limpo}"
        
        response = requests.get(url, timeout=10)
        
        # A BrasilAPI retorna erro 404 para CEP não encontrado, que será capturado abaixo
        response.raise_for_status() 
        
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"erro": "CEP não encontrado"}
        return {"erro": f"Erro HTTP: {e}"}
    except requests.exceptions.RequestException:
        return {"erro": "Erro na requisição (verifique firewall/internet)"}
    except Exception as e:
        return {"erro": f"Erro inesperado: {e}"}

def processar_planilha_com_retomada():
    """Lê a planilha, consulta os CEPs e salva o resultado com retomada automática."""
    try:
        df_original = pd.read_excel(ARQUIVO_ENTRADA)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    # Lógica de retomada (continua a mesma)
    if os.path.exists(ARQUIVO_SAIDA):
        print(f"Arquivo de saída '{ARQUIVO_SAIDA}' encontrado. Tentando retomar o progresso...")
        df_resultado = pd.read_excel(ARQUIVO_SAIDA)
        df_original[NOME_COLUNA_CEP] = df_original[NOME_COLUNA_CEP].astype(str)
        df_resultado[NOME_COLUNA_CEP] = df_resultado[NOME_COLUNA_CEP].astype(str)
        ceps_processados = set(df_resultado[df_resultado['Status'] == 'Sucesso'][NOME_COLUNA_CEP])
        print(f"{len(ceps_processados)} CEPs já processados encontrados.")
    else:
        print(f"Arquivo de saída não encontrado. Iniciando do zero.")
        df_resultado = pd.DataFrame()
        ceps_processados = set()
    
    df_para_processar = df_original[~df_original[NOME_COLUNA_CEP].astype(str).isin(ceps_processados)]

    if df_para_processar.empty:
        print("Todos os CEPs já foram processados com sucesso. Tarefa concluída.")
        return
    
    total_ceps = len(df_para_processar)
    print(f"Iniciando consulta de {total_ceps} CEPs restantes na BrasilAPI...")

    novos_resultados = []
    for index, row in df_para_processar.iterrows():
        cep_original = str(row[NOME_COLUNA_CEP])
        endereco = consultar_cep_brasilapi(cep_original) # <<< Chamando a nova função
        
        linha_resultado = row.to_dict()
        
        # <<< MUDANÇA PRINCIPAL: MAPEANDO OS CAMPOS DA BRASILAPI >>>
        if 'erro' not in endereco:
            linha_resultado.update({
                'Logradouro': endereco.get('street', ''),
                'Bairro': endereco.get('neighborhood', ''),
                'Cidade': endereco.get('city', ''),
                'UF': endereco.get('state', ''),
                'Status': 'Sucesso'
            })
        else:
            linha_resultado['Status'] = endereco.get('erro', 'Erro desconhecido')
            # Garante que os outros campos fiquem em branco em caso de erro
            linha_resultado.update({'Logradouro': '', 'Bairro': '', 'Cidade': '', 'UF': ''})

        novos_resultados.append(linha_resultado)
        
        print(f"Processando CEP {len(novos_resultados)}/{total_ceps}: {cep_original} - Status: {linha_resultado['Status']}")
        time.sleep(0.05) # Mantemos a pausa por boa prática

        # Lógica de salvamento automático (continua a mesma)
        if len(novos_resultados) % LOTE_SALVAMENTO == 0:
            print(f"\n--- Salvando lote de {LOTE_SALVAMENTO} registros... ---")
            df_lote = pd.DataFrame(novos_resultados)
            df_resultado = pd.concat([df_resultado, df_lote], ignore_index=True)
            df_resultado.to_excel(ARQUIVO_SAIDA, index=False)
            novos_resultados = []

    # Salva os registros restantes
    if novos_resultados:
        print("\n--- Salvando registros finais... ---")
        df_lote = pd.DataFrame(novos_resultados)
        df_resultado = pd.concat([df_resultado, df_lote], ignore_index=True)
        df_resultado.to_excel(ARQUIVO_SAIDA, index=False)

    print(f"\nProcesso concluído! Os dados foram salvos no arquivo '{ARQUIVO_SAIDA}'.")

# --- Inicia a execução do script ---
if __name__ == "__main__":
    processar_planilha_com_retomada()
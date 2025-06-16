import pandas as pd
import requests
import time

# --- CONFIGURAÇÕES DO TESTE ---
ARQUIVO_ENTRADA = 'ceps.xlsx'
NOME_COLUNA_CEP = 'CEP'
NUMERO_DE_TESTES = 5 
# -----------------------------

def consultar_cep_brasilapi(cep):
    """Consulta um único CEP na BrasilAPI."""
    try:
        cep_limpo = ''.join(filter(str.isdigit, str(cep)))
        if len(cep_limpo) != 8:
            return {"erro": "Formato de CEP inválido"}

        url = f"https://brasilapi.com.br/api/cep/v2/{cep_limpo}"
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"erro": "CEP não encontrado"}
        return {"erro": f"Erro HTTP: {e}"}
    except requests.exceptions.RequestException:
        return {"erro": "Erro na requisição"}
    except Exception as e:
        return {"erro": f"Erro inesperado: {e}"}

def testar_consulta_no_terminal():
    """Lê as primeiras linhas da planilha, consulta os CEPs na BrasilAPI e imprime no terminal."""
    try:
        df_completo = pd.read_excel(ARQUIVO_ENTRADA)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    df_teste = df_completo.head(NUMERO_DE_TESTES)
    print(f"--- INICIANDO TESTE COM OS {NUMERO_DE_TESTES} PRIMEIROS CEPS NA BRASILAPI ---")

    resultados = []
    for index, row in df_teste.iterrows():
        cep_original = row[NOME_COLUNA_CEP]
        print(f"Consultando CEP: {cep_original}...")
        
        endereco = consultar_cep_brasilapi(cep_original)
        
        linha_resultado = row.to_dict()
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
            linha_resultado.update({'Logradouro': '', 'Bairro': '', 'Cidade': '', 'UF': ''})
            
        resultados.append(linha_resultado)
        
        # <<< MUDANÇA PRINCIPAL: AUMENTANDO A PAUSA PARA 1 SEGUNDO >>>
        time.sleep(1) 

    df_resultado = pd.DataFrame(resultados)
    print("\n--- RESULTADO DO TESTE (BrasilAPI) ---")
    print(df_resultado)
    print("--------------------------------------")

if __name__ == "__main__":
    testar_consulta_no_terminal()
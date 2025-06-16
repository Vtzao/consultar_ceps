import pandas as pd
import requests
import warnings

# --- CONFIGURAÇÕES DO TESTE ---
ARQUIVO_ENTRADA = 'ceps.xlsx'
NOME_COLUNA_CEP = 'CEP'
NUMERO_DE_TESTES = 5
# -----------------------------

# --- CONFIGURAÇÕES DE REDE CORPORATIVA ---
# Se sua empresa usa um proxy, pergunte ao seu time de TI o endereço e coloque aqui.
# Exemplo: 'http://usuario:senha@proxy.suaempresa.com:8080'
# Se não usar proxy, deixe como None.
PROXY = None 

# Mude para False apenas se encontrar erros de certificado SSL (SSLError).
VERIFICAR_SSL = True
# ----------------------------------------


def consultar_cep(cep):
    """Consulta um único CEP na API do ViaCEP, com suporte a proxy e SSL."""
    
    # Configuração do proxy para a requisição
    proxies = {
        'http': PROXY,
        'https': PROXY,
    } if PROXY else None

    try:
        cep_limpo = str(cep).strip().replace('.', '').replace('-', '')
        if len(cep_limpo) != 8 or not cep_limpo.isdigit():
            return {"erro": "Formato de CEP inválido"}

        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        
        # Desativa avisos de segurança apenas se VERIFICAR_SSL for False
        if not VERIFICAR_SSL:
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')

        response = requests.get(
            url, 
            timeout=15, 
            proxies=proxies,       # <<< Adicionado suporte a proxy
            verify=VERIFICAR_SSL   # <<< Adicionado controle de SSL
        )
        
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ProxyError as e:
        return {"erro": f"Erro de Proxy: {e}"}
    except requests.exceptions.SSLError as e:
        return {"erro": f"Erro de SSL: {e}"}
    except requests.RequestException:
        # Este erro é genérico. As causas comuns são firewall ou falta de internet.
        return {"erro": "Erro na requisição (verifique firewall/internet)"}
    except Exception as e:
        return {"erro": f"Erro inesperado: {e}"}

def testar_consulta_no_terminal():
    """Lê as primeiras linhas da planilha, consulta os CEPs e imprime o resultado no terminal."""
    try:
        df_completo = pd.read_excel(ARQUIVO_ENTRADA)
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    df_teste = df_completo.head(NUMERO_DE_TESTES)
    print(f"--- INICIANDO TESTE COM OS {NUMERO_DE_TESTES} PRIMEIROS CEPS ---")

    resultados = []
    for index, row in df_teste.iterrows():
        cep_original = row[NOME_COLUNA_CEP]
        print(f"Consultando CEP: {cep_original}...")
        
        endereco = consultar_cep(cep_original)
        
        linha_resultado = row.to_dict()
        if not endereco.get('erro'):
            linha_resultado['Logradouro'] = endereco.get('logradouro', '')
            linha_resultado['Bairro'] = endereco.get('bairro', '')
            linha_resultado['Cidade'] = endereco.get('localidade', '')
            linha_resultado['UF'] = endereco.get('uf', '')
            linha_resultado['Status'] = 'Sucesso'
        else:
            linha_resultado['Logradouro'] = ''
            linha_resultado['Bairro'] = ''
            linha_resultado['Cidade'] = ''
            linha_resultado['UF'] = ''
            linha_resultado['Status'] = endereco.get('erro')
            
        resultados.append(linha_resultado)

    df_resultado = pd.DataFrame(resultados)
    print("\n--- RESULTADO DO TESTE ---")
    print(df_resultado)
    print("--------------------------")

if __name__ == "__main__":
    testar_consulta_no_terminal()
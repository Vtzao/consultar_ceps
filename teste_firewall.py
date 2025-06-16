import requests
import time

def testar_conexao_geral():
    """
    Tenta se conectar 10 vezes a uma API de teste global (JSONPlaceholder)
    para diagnosticar bloqueios de firewall.
    """
    print("--- INICIANDO TESTE DE CONEXÃO DE REDE GERAL ---")
    print("Alvo: JSONPlaceholder (API de testes global)\n")
    
    sucessos = 0
    falhas = 0
    
    # Vamos tentar acessar 10 recursos diferentes (posts de 1 a 10)
    for i in range(1, 11):
        url = f"https://jsonplaceholder.typicode.com/posts/{i}"
        
        try:
            # Tenta fazer a requisição com um timeout de 5 segundos
            response = requests.get(url, timeout=5)
            
            # Verifica se a resposta foi bem-sucedida (código 200)
            if response.status_code == 200:
                print(f"Tentativa {i:02d}: SUCESSO! (Conexão com {url} OK)")
                sucessos += 1
            else:
                # Se o status não for 200, consideramos uma falha
                print(f"Tentativa {i:02d}: FALHA! (Servidor respondeu com erro: {response.status_code})")
                falhas += 1

        except requests.exceptions.RequestException as e:
            # Se a conexão nem sequer pôde ser estabelecida, é o erro que queremos pegar
            print(f"Tentativa {i:02d}: FALHA NA REQUISIÇÃO! (Não foi possível conectar)")
            falhas += 1
        
        # Pausa entre as tentativas
        time.sleep(0.5)

    print("\n--- TESTE CONCLUÍDO ---")
    print(f"Resultados: {sucessos} Sucessos, {falhas} Falhas.")


if __name__ == "__main__":
    testar_conexao_geral()
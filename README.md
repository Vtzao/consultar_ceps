Consulta de CEPs em Massa com Python
Este projeto contém um script Python (consultar_ceps_viacep.py) que automatiza a consulta de múltiplos CEPs a partir de uma planilha Excel. Ele utiliza a API pública do ViaCEP para buscar os dados de endereço e, ao final, salva todos os resultados em uma nova planilha.

✨ Funcionalidades
Lê uma lista de CEPs de uma planilha Excel (.xlsx).
Consulta cada CEP na API pública ViaCEP.
Trata erros de formato e CEPs não encontrados.
Salva os resultados completos (Logradouro, Bairro, Cidade, UF e Status) em uma nova planilha Excel.
📋 Pré-requisitos
Python 3.6 ou superior.
🚀 Instalação e Configuração
Siga os passos abaixo para preparar o ambiente e rodar o script.

1. Instale o Python

Faça o download da versão mais recente do Python em python.org.
Importante: Durante a instalação no Windows, marque a caixa de seleção "Add Python to PATH" ou "Adicionar Python ao PATH".
2. Instale as Dependências

Com o Python instalado, abra seu terminal (Prompt de Comando, PowerShell ou Terminal) na pasta deste projeto.
Execute o seguinte comando para instalar as bibliotecas necessárias:
Bash

pip install pandas requests openpyxl
3. Prepare a Planilha de Entrada

Na mesma pasta do script, coloque sua planilha com a lista de CEPs.
O arquivo deve se chamar ceps.xlsx.
A coluna que contém os CEPs deve ter o cabeçalho CEPS.
▶️ Como Executar
Com tudo configurado, a execução é simples:

Abra seu terminal na pasta do projeto.
Execute o script com o seguinte comando:
Bash

python consultar_ceps_viacep.py
Aguarde o processo ser concluído. O script exibirá o progresso no terminal.
📄 O Resultado
Ao final da execução, um novo arquivo chamado enderecos_resultados.xlsx será criado na mesma pasta. Ele conterá as seguintes colunas:

CEP_Consultado
Logradouro
Bairro
Cidade
UF
Status (informando "Sucesso", "CEP não encontrado" ou outro erro)
⚠️ Tratamento de Erros
O script foi projetado para lidar com os erros mais comuns da API ViaCEP:

CEP com Formato Inválido: CEPs com mais ou menos de 8 dígitos, ou que contenham letras e espaços, serão identificados pelo script e marcados com o status "Formato de CEP inválido", sem fazer uma chamada desnecessária à API.
CEP Válido, mas Inexistente: Se um CEP tiver 8 dígitos mas não for encontrado na base de dados do ViaCEP (ex: "99999999"), o script receberá a confirmação da API e marcará o status como "CEP não encontrado".
✒️ Créditos
Este projeto foi desenvolvido por:

Vitor Pereira

GitHub: https://github.com/Vtzao

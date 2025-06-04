# 📄 Sistema de Processamento e Validação de Faturas

Este projeto apresenta um sistema automatizado para extração, edição e validação de dados de faturas em formato PDF, utilizando inteligência artificial (LLMs) para a extração e Pydantic para validação robusta dos campos. A interface de usuário é desenvolvida com Streamlit, proporcionando uma experiência interativa para revisão e correção dos dados.

## ✨ Funcionalidades Principais

* **Extração de Dados com LLM:** Utiliza um modelo de linguagem grande (LLM) (presumivelmente `gemini-1.5-flash` via `google-adk`) para extrair informações chave de documentos PDF de faturas (tipo de documento, ID, data, valores financeiros, dados do fornecedor e cliente).
* **Interface Interativa (Streamlit):** Uma aplicação web amigável permite o upload de PDFs, visualização dos dados extraídos e edição manual.
* **Validação de Dados Robustas:** Implementa validações rigorosas (com base em `invoice_validator.py` e Pydantic) para garantir a integridade e o formato correto dos dados extraídos (datas, moedas, NIFs, valores financeiros, etc.).
* **Feedback Visual Claro:** Fornece indicadores visuais (verde, amarelo, vermelho) para o status de validação de cada campo, com mensagens detalhadas sobre os erros ou avisos.
* **Resumo de Validação:** Apresenta um painel de resumo com o status geral da validação da fatura.
* **Configuração Dinâmica do Formulário:** Permite selecionar quais campos devem ser exibidos e editados na interface, através de presets ou seleção personalizada.
* **Exportação de Dados:** Possibilita exportar os dados da fatura (editados e validados) para o formato JSON.

## 🚀 Como Executar o Projeto

### Pré-requisitos

* Python 3.8+
* `pip` (gerenciador de pacotes Python)
* **Servidor LLM:** Este projeto interage com um servidor de LLM para a extração de dados. O `agent.py` demonstra a configuração de um `Agent` do Google ADK. Para a execução da UI, um endpoint acessível (e.g., `http://localhost:8000/run`) que processa PDFs e retorna os dados de fatura é necessário.

### Configuração e Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/invoice-processor-project.git](https://github.com/SEU_USUARIO/invoice-processor-project.git)
    cd invoice-processor-project
    ```
    *(Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub)*

2.  **Crie um Ambiente Virtual (Altamente Recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuração de Variáveis de Ambiente (Opcional, mas Recomendado):**
    Se seu agente ou API exigir chaves, crie um arquivo `.env` na raiz do projeto:
    ```
    GOOGLE_API_KEY="SUA_CHAVE_API"
     # Outras variáveis, se necessário
    ```
    Lembre-se de que o arquivo `.env` está configurado para ser ignorado pelo Git (`.gitignore`).

### Executando a Aplicação

1.  **Certifique-se de que seu Servidor LLM está Ativo:**
    Antes de iniciar a UI, o endpoint para extração de dados (conforme configurado em `ui5.py`, e.g., `http://localhost:8000/run`) deve estar acessível e funcional. A implementação em `agent.py` demonstra a utilização do Google ADK, mas a forma de expor este agente como um serviço HTTP deve ser feita separadamente.

2.  **Execute a Interface do Streamlit:**
    Navegue até a pasta `src` e inicie a aplicação:
    ```bash
    cd src
    cd Agents
    adk api_server
    novo terminal
    ir para src outra vez
    streamlit run ui5.py
    ```
    Isso abrirá a aplicação no seu navegador padrão (geralmente `http://localhost:8501`).

## 📁 Estrutura do Projeto

invoice-processor-project/
├── .github/              # Configurações do GitHub (ex: workflows de CI/CD)
├── src/                  # Código fonte principal da aplicação
│   ├── agent.py          # Definição do Agente LLM para extração de faturas
│   ├── invoice_validator.py # Lógica de validação de dados com Pydantic
│   ├── styles.py         # Estilos CSS personalizados para a interface
│   └── ui5.py            # A interface de usuário principal (Streamlit)
├── docs/                 # Documentação adicional do projeto (opcional)
├── samples/              # Exemplos de arquivos PDF de faturas
│   ├── Fatura.pdf
│   └── ... (outros exemplos)
├── archive/              # Código e UIs de versões anteriores (não ativamente mantidas)
│   ├── pydantic_val.py   # Versão anterior do validador de Pydantic
│   └── ui/               # UIs de versões anteriores (ui, ui2, ui3, ui4)
│       ├── ui (WORKING).py
│       ├── ui2.py
│       ├── ui3(Latest).py
│       └── ui4.py
├── .gitignore            # Arquivos e pastas a serem ignorados pelo Git
├── requirements.txt      # Dependências do projeto Python
└── README.md             # Este arquivo


## 🛠️ Tecnologias Utilizadas

* **Python 3.8+**
* **Streamlit:** Para a criação da interface de usuário interativa.
* **Pydantic:** Para a modelagem e validação de dados de forma declarativa.
* **Requests:** Para comunicação HTTP com serviços externos (como o servidor LLM).
* **Google ADK (Agent Development Kit):** Para a construção de agentes de IA para processamento de documentos.

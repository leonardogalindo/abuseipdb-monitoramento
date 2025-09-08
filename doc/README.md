# blocklist-abuseipdb - Análise de IPs Críticos

## Descrição do Projeto

Este projeto Python tem como objetivo monitorar e analisar endereços IP de provedores específicos (atualmente focado em Locaweb e KingHost) que aparecem em listas de denúncias públicas (blocklists), como a do AbuseIPDB. Ele enriquece esses dados com informações adicionais (como hostname e detalhes de reputação do AbuseIPDB) e notifica a equipe de segurança (SOC) por e-mail sobre novos IPs críticos, facilitando a identificação e mitigação de possíveis ameaças.

## Funcionalidades

*   **Download Automático da Blocklist:** Baixa a blocklist atualizada diariamente de uma fonte confiável.
*   **Filtragem Inteligente:** Utiliza expressões regulares (regex) para identificar IPs de provedores específicos (ex: Locaweb, KingHost) diretamente no arquivo da blocklist, otimizando as consultas à API.
*   **Regra de Histórico e 30 Dias:** Mantém um histórico de IPs já analisados e reporta apenas IPs novos ou aqueles que não foram vistos em denúncias nos últimos 30 dias.
*   **Integração com AbuseIPDB:** Consulta a API do AbuseIPDB para obter detalhes de reputação (categorias de abuso e comentários recentes) para os IPs identificados.
*   **Notificação por E-mail:** Envia e-mails formais para a equipe SOC com um resumo dos IPs críticos encontrados, incluindo um anexo com o relatório detalhado em formato JSON.
*   **Tratamento Especial KingHost:** Identifica IPs da KingHost (baseado no hostname) e os reporta em um arquivo e e-mail separados, com assunto específico.
*   **Estrutura Modular e Clean Code:** Projeto organizado em módulos (`main.py`, `analisador_locaweb.py`, `abuseipdb_checker.py`, `notificador_email.py`, `settings.py`) seguindo boas práticas de programação orientada a objetos e Clean Code.
*   **Logging Detalhado:** Configuração de logging robusta que registra eventos em console e em arquivo (`logs/settings.log`) para depuração e auditoria.
*   **Gerenciamento Seguro de Credenciais:** Utiliza variáveis de ambiente (`.env`) para armazenar chaves de API e credenciais de e-mail, mantendo-as fora do código-fonte.

## Pré-requisitos

*   Python 3.x (versão 3.8 ou superior recomendada)
*   `pip` (gerenciador de pacotes do Python)
*   Acesso à internet para baixar a blocklist e consultar as APIs.
*   Uma chave de API do AbuseIPDB (pode ser obtida em [AbuseIPDB](https://www.abuseipdb.com/)).
*   Credenciais de um servidor SMTP para envio de e-mails.

## Configuração do Ambiente

1.  **Clone o repositório (se aplicável):**
    ```bash
    # cd /caminho/para/seu/diretorio
    # git clone [URL_DO_SEU_REPOSITORIO]
    # cd blocklist-abuseipdb
    ```
    *(Se você recebeu os arquivos diretamente, apenas navegue até o diretório `blocklist-abuseipdb`)*

2.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o arquivo `.env`:**
    Crie um arquivo chamado `.env` na **raiz do projeto** (`/home/leonardogalindo/blocklist-abuseipdb/.env`) com o seguinte conteúdo, substituindo os valores pelos seus dados reais:

    ```ini
    ABUSEIPDB_API_KEY=SUA_CHAVE_API_DO_ABUSEIPDB
    EMAIL_SMTP_SERVER=seu_servidor_smtp.com
    EMAIL_SMTP_PORT=587
    EMAIL_SENDER=seu_email@exemplo.com
    EMAIL_PASSWORD=sua_senha_do_email_ou_app_password
    EMAIL_RECEIVER=email_do_soc@exemplo.com
    ```
    *   **Importante:** Para serviços como Gmail com 2FA, use uma **senha de aplicativo** gerada nas configurações de segurança da sua conta, não sua senha principal.

## Estrutura do Projeto

```
blocklist-abuseipdb/
├── main.py
├── .env
├── .gitignore
├── src/
│   ├── analisador_locaweb.py
│   ├── abuseipdb_checker.py
│   ├── notificador_email.py
│   └── settings.py
├── data/
│   ├── historico_locaweb.json
│   ├── novos_locaweb_diario.json
│   └── novos_kinghost_diario.json
├── logs/
│   └── settings.log
├── tests/
│   ├── test_analisador_locaweb.py
│   ├── test_abuseipdb_checker.py
│   └── test_notificador_email.py
└── doc/
    └── README.md
```

*   `main.py`: Ponto de entrada principal da aplicação.
*   `src/`: Contém o código-fonte modularizado.
*   `data/`: Armazena os arquivos JSON de histórico e relatórios diários.
*   `logs/`: Armazena os logs detalhados da execução.
*   `tests/`: Contém os testes unitários do projeto.
*   `doc/`: Contém a documentação do projeto.

## Como Executar

Após configurar o ambiente e o arquivo `.env`:

1.  **Navegue até o diretório raiz do projeto:**
    ```bash
    cd /home/leonardogalindo/blocklist-abuseipdb
    ```

2.  **Execute o script principal usando o interpretador do ambiente virtual:**
    ```bash
    /home/leonardogalindo/blocklist-abuseipdb/.venv/bin/python3 main.py
    ```
    *(Alternativamente, se você ativou o ambiente virtual com `source .venv/bin/activate`, pode simplesmente usar `python main.py`)*

## Como Executar Testes

1.  **Navegue até o diretório raiz do projeto:**
    ```bash
    cd /home/leonardogalindo/blocklist-abuseipdb
    ```

2.  **Execute os testes usando pytest (com o ambiente virtual ativado):**
    ```bash
    pytest tests/
    ```

## Relatórios Gerados

Os relatórios diários e o histórico são salvos na pasta `data/`:

*   `historico_locaweb.json`: Contém o histórico completo de todos os IPs da Locaweb já processados, com a data da última verificação.
*   `novos_locaweb_diario.json`: Contém os IPs da Locaweb (que não são KingHost) encontrados na execução atual que são novos ou não foram vistos nos últimos 30 dias.
*   `novos_kinghost_diario.json`: Contém os IPs da KingHost encontrados na execução atual que são novos ou não foram vistos nos últimos 30 dias.

## Logging

Os logs detalhados da execução são gravados em `logs/settings.log`. Este arquivo é útil para depuração e para acompanhar o processamento dos IPs. Mensagens informativas também são exibidas no console.

---


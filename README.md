#  AbuseIPDB Monitoramento 🛡️

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Um sistema de monitoramento que automatiza a verificação de reputação de endereços IP, notificando sobre IPs críticos da Locaweb e KingHost.

---

## 📜 Índice

- [Sobre](#sobre-o-projeto-)
- [Funcionalidades](#funcionalidades-)
- [Instalação](#como-instalar-)
- [Como Usar](#como-usar-)
- [Contribuição](#como-contribuir-)
- [Licença](#licença-)

---

## 📖 Sobre o Projeto <a name="sobre-o-projeto"></a>

Este projeto foi criado para automatizar o processo de verificação de reputação de IPs, focando em provedores específicos como Locaweb e KingHost. Ele baixa uma blocklist, consulta a API do AbuseIPDB e envia relatórios diários por e-mail, ajudando a identificar ameaças de forma proativa.

## ✨ Funcionalidades <a name="funcionalidades"></a>

-   📥 **Download de Blocklist**: Baixa automaticamente listas de IPs atualizadas.
-   🔍 **Filtragem por Provedor**: Filtra e separa IPs pertencentes à Locaweb e KingHost.
-   📊 **Consulta ao AbuseIPDB**: Verifica a reputação de cada IP usando a API do AbuseIPDB.
-   📧 **Notificações por E-mail**: Envia relatórios diários com os IPs críticos encontrados.
-   ⚙️ **Configuração Flexível**: Use variáveis de ambiente para configurar a aplicação.

## 🚀 Como Instalar <a name="como-instalar"></a>

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/abuseipdb-monitoramento.git
    cd abuseipdb-monitoramento
    ```

2.  **Crie um ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:
    ```env
    ABUSEIPDB_API_KEY=sua_chave_de_api
    EMAIL_HOST=smtp.example.com
    EMAIL_PORT=587
    EMAIL_USER=seu_email@example.com
    EMAIL_PASSWORD=sua_senha
    ```

## 🛠️ Como Usar <a name="como-usar"></a>

Para executar o monitoramento, basta rodar o script principal:

```bash
python main.py
```

O script executará todas as etapas, desde o download da blocklist até o envio do e-mail com os resultados.

## 🤝 Como Contribuir <a name="como-contribuir"></a>

Contribuições são bem-vindas! Se você tiver alguma ideia ou sugestão, siga os passos abaixo:

1.  **Faça um Fork** do projeto.
2.  **Crie uma Branch** para sua feature (`git checkout -b feature/nova-feature`).
3.  **Faça o Commit** de suas mudanças (`git commit -m 'feat: Adiciona nova feature'`).
4.  **Faça o Push** para a Branch (`git push origin feature/nova-feature`).
5.  **Abra um Pull Request**.

## 📄 Licença <a name="licença"></a>

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

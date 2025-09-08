# -*- coding: utf-8 -*-

import logging
import os
import sys

from dotenv import load_dotenv  # Importa load_dotenv

# Adiciona o diretório 'src' ao path para permitir importações diretas
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_path)

# Carrega as variáveis do .env para o ambiente
load_dotenv()

from analisador_locaweb import AnalisadorLocaweb
# Agora podemos importar os módulos de 'src'
from settings import LOG_CONFIG_DICT

# Configura o logging assim que a aplicação inicia
logging.config.dictConfig(LOG_CONFIG_DICT)
logger = logging.getLogger("locaweb_analyzer")  # Pega o logger principal


def main():
    """
    Função principal que orquestra a execução do projeto.
    """
    logger.info("Aplicação iniciada pelo main.py")

    try:
        analisador = AnalisadorLocaweb(
            url_blocklist="https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/refs/heads/main/abuseipdb-s100-14d.ipv4",
            arquivo_historico="data/historico_locaweb.json",
            arquivo_diario="data/novos_locaweb_diario.json",  # Para IPs Locaweb (outros)
            arquivo_diario_kinghost="data/novos_kinghost_diario.json",  # Para IPs KingHost
        )
        analisador.executar()
    except Exception:
        logger.critical("Ocorreu um erro fatal na aplicação!", exc_info=True)
        sys.exit(1)

    logger.info("Aplicação finalizada com sucesso.")


if __name__ == "__main__":
    main()

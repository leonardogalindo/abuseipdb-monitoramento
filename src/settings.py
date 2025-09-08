import logging.config
import os

# --- Configuração de Log para DESENVOLVIMENTO ---
# (Salva em arquivo, nível DEBUG, verboso)
LOG_CONFIG_DEV = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file_formatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "stream_formatter": {"format": "%(levelname)s - %(message)s"},
    },
    "handlers": {
        "fileHandler": {
            "class": "logging.FileHandler",
            "formatter": "file_formatter",
            "filename": os.path.join("logs", "settings.log"),
            "encoding": "utf-8",
            "level": "DEBUG",
        },
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "stream_formatter",
            "level": "INFO",
        },
    },
    "root": {"handlers": ["fileHandler", "consoleHandler"], "level": "DEBUG"},
    "loggers": {
        "requests": {"handlers": ["fileHandler"], "level": "WARNING", "propagate": False}
    },
}

# --- Configuração de Log para PRODUÇÃO ---
# (Saída no console, nível INFO, formato estruturado)
LOG_CONFIG_PROD = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "production_formatter": {
            "format": "%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] - %(message)s",
        },
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "production_formatter",
            "level": "INFO",
        },
    },
    "root": {"handlers": ["consoleHandler"], "level": "INFO"},
    "loggers": {
        "requests": {"handlers": ["consoleHandler"], "level": "WARNING", "propagate": False}
    },
}

# --- Seleção da Configuração ---
# Verifica a variável de ambiente 'APP_ENV'.
# Se for 'production', usa a config de produção. Caso contrário, usa a de desenvolvimento.
if os.getenv("APP_ENV") == "production":
    LOG_CONFIG_DICT = LOG_CONFIG_PROD
    print("Usando configuração de log de PRODUÇÃO.")
else:
    LOG_CONFIG_DICT = LOG_CONFIG_DEV
    print("Usando configuração de log de DESENVOLVIMENTO.")

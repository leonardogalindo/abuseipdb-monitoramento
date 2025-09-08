# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import requests

# load_dotenv() não é mais chamado aqui, pois o main.py fará isso.

logger = logging.getLogger(__name__)


class AbuseIPDBChecker:
    """
    Responsável por verificar a reputação de um IP na API do AbuseIPDB.
    """

    # Dicionário para mapear IDs de categoria para nomes legíveis
    # Fonte: https://www.abuseipdb.com/categories
    CATEGORIAS = {
        3: "Fraud Orders",
        4: "DDoS Attack",
        5: "FTP Brute-Force",
        6: "Ping of Death",
        7: "Phishing",
        8: "Fraud VoIP",
        9: "Open Proxy",
        10: "Web Spam",
        11: "Email Spam",
        12: "Blog Spam",
        13: "VPN IP",
        14: "Port Scan",
        15: "Hacking",
        16: "SQL Injection",
        17: "Spoofing",
        18: "Brute-Force",
        19: "Bad Web Bot",
        20: "Exploited Host",
        21: "Web App Attack",
        22: "SSH",
        23: "IoT Targeted",
    }

    def __init__(self):
        self.api_key = os.getenv("ABUSEIPDB_API_KEY")
        if not self.api_key:
            logger.critical(
                "A chave da API do AbuseIPDB não foi encontrada nas variáveis de ambiente!"
            )
            raise ValueError("Chave da API não configurada.")
        self.base_url = "https://api.abuseipdb.com/api/v2/reports"
        self.headers = {"Accept": "application/json", "Key": self.api_key}

    def _formatar_comentario(self, comentario):
        """Limpa e formata um comentário para melhor legibilidade."""
        return " ".join(comentario.strip().split())

    def _formatar_data(self, data_str):
        """Converte a data do formato ISO para o formato brasileiro."""
        try:
            dt_obj = datetime.fromisoformat(data_str.replace("+00:00", ""))
            return dt_obj.strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            logger.debug(f"Não foi possível formatar a data: {data_str}")
            return data_str

    def verificar_ip(self, ip_address):
        """
        Busca os relatórios de um IP e retorna as informações formatadas.
        """
        params = {"ipAddress": ip_address, "maxAgeInDays": 30, "perPage": 5}

        logger.debug(f"Consultando AbuseIPDB para o IP: {ip_address}")
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            dados = response.json().get("data", {})

            if not dados or not dados.get("results"):
                logger.info(
                    f"Nenhum relatório encontrado para o IP {ip_address} no AbuseIPDB."
                )
                return {"categorias_reportadas": [], "comentarios_recentes": []}

            categorias_ids = set()
            for relatorio in dados.get("results", []):
                for cat_id in relatorio.get("categories", []):
                    categorias_ids.add(cat_id)

            categorias_nomes = [
                self.CATEGORIAS.get(cat_id, f"Desconhecida ({cat_id})")
                for cat_id in sorted(list(categorias_ids))
            ]

            comentarios = []
            for relatorio in dados.get("results", []):
                comentario_formatado = self._formatar_comentario(relatorio["comment"])
                data_formatada = self._formatar_data(relatorio["reportedAt"])
                comentarios.append(f"[{data_formatada}] {comentario_formatado}")

            return {
                "categorias_reportadas": categorias_nomes,
                "comentarios_recentes": comentarios,
            }

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Erro ao consultar a API do AbuseIPDB para o IP {ip_address}: {e}"
            )
            return {
                "categorias_reportadas": ["Erro na consulta"],
                "comentarios_recentes": [],
            }

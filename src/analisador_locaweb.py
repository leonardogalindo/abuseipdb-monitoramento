# -*- coding: utf-8 -*-

import requests
import json
import os
import logging
import time
import re
from datetime import datetime, timedelta

# Não importa settings aqui, pois o logging é configurado no main.py
# e este módulo obtém o logger pelo nome.

logger = logging.getLogger(__name__)

# Importa o NotificadorEmail
from src.notificador_email import NotificadorEmail

from src.abuseipdb_checker import AbuseIPDBChecker

class AnalisadorLocaweb:
    """
    Busca IPs da Locaweb em uma blocklist usando regex, obtém informações
    adicionais e aplica a regra de 30 dias para reportar IPs.
    """

    def __init__(self, url_blocklist, arquivo_historico, arquivo_diario, arquivo_diario_kinghost):
        self.url_blocklist = url_blocklist
        # Os caminhos já vêm resolvidos do main.py
        self.arquivo_historico = arquivo_historico
        self.arquivo_diario = arquivo_diario # Este será para Locaweb (outros)
        self.arquivo_diario_kinghost = arquivo_diario_kinghost # Novo arquivo para KingHost
        self.provedor_alvo = "Locaweb Serviços de Internet S/A"
        self.hoje = datetime.now()
        self.s = requests.Session()
        self.s.headers.update({'User-Agent': 'Mozilla/5.0'})

    def _carregar_historico(self):
        if not os.path.exists(self.arquivo_historico):
            return {}
        try:
            with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if not conteudo: # Se o arquivo estiver vazio
                    logger.debug(f"Arquivo {self.arquivo_historico} está vazio. Retornando histórico vazio.")
                    return {}
                f.seek(0) # Volta o ponteiro para o início do arquivo
                dados = json.load(f)
                return {item['ip']: item for item in dados}
        except (json.JSONDecodeError, IOError):
            logger.debug("Falha ao carregar histórico JSON (arquivo inválido ou erro de I/O).", exc_info=True)
            return {}

    def _salvar_json(self, caminho_arquivo, dados):
        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            logger.info(f"Dados salvos com sucesso em: {caminho_arquivo}")
        except IOError:
            logger.debug(f"Erro ao salvar o arquivo {caminho_arquivo}.", exc_info=True)

    def baixar_e_filtrar_blocklist(self):
        logger.info(f"Baixando e filtrando a blocklist de: {self.url_blocklist}")
        try:
            r = self.s.get(self.url_blocklist)
            r.raise_for_status()
            
            regex = re.compile(r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+.*?\s+(AS\d+)\s+(Locaweb[\w\s.-]*S\/A)", re.MULTILINE)
            
            matches = regex.findall(r.text)
            
            ips_encontrados = []
            for ip, asn, provedor in matches:
                ips_encontrados.append({
                    "ip": ip,
                    "asn": asn,
                    "provedor": provedor.strip()
                })
            
            logger.info(f"Encontrados {len(ips_encontrados)} IPs da Locaweb diretamente no arquivo.")
            return ips_encontrados
        except requests.exceptions.RequestException:
            logger.debug("Erro ao baixar a blocklist.", exc_info=True)
            return []

    def obter_hostname(self, ip):
        logger.debug(f"Consultando API para obter o hostname do IP: {ip}")
        url_api = f"http://ip-api.com/json/{ip}?fields=status,message,reverse"
        try:
            r = self.s.get(url_api)
            r.raise_for_status()
            dados = r.json()
            if dados.get("status") == "success":
                return dados.get('reverse', 'N/A')
            return 'N/A'
        except requests.exceptions.RequestException:
            logger.debug(f"Falha ao obter hostname para o IP {ip}.", exc_info=True)
            return 'N/A'

    def _construir_corpo_email_notificacao(self, ips_reportados, tipo_relatorio):
        data_atual = self.hoje.strftime("%d/%m/%Y")
        assunto_base = "Relatório Diário de IPs Críticos"

        if tipo_relatorio == "KingHost":
            assunto_completo = f"Novos IPs da KingHost Reportados no AbuseIPDB - {data_atual}"
            titulo_ips = "IPs da KingHost Reportados:"
        else: # Locaweb (outros)
            assunto_completo = f"Novos IPs da Locaweb Reportados no AbuseIPDB - {data_atual}"
            titulo_ips = "IPs da Locaweb Reportados:"

        corpo = f"""
        <html>
        <body>
            <p>Prezada Equipe SOC,</p>
            <p>Segue o {assunto_completo}, referente à data de {data_atual}.</p>
            <p><b>Resultado da análise:</b></p>
            <p>✅ IPs com reputação crítica foi identificado nas últimas 24 horas.</p>
            <p>Conforme procedimento de rotina, recomendamos a análise dos IPs listados para identificação e mitigação de possíveis ameaças à segurança da rede.</p>
            <p><b>{titulo_ips}</b></p>
            <ul>
        """
        for ip_info in ips_reportados:
            corpo += f"<li><b>IP:</b> {ip_info.get('ip', 'N/A')}<br>"
            corpo += f"<b>Provedor:</b> {ip_info.get('provedor', 'N/A')}<br>"
            corpo += f"<b>Hostname:</b> {ip_info.get('hostname', 'N/A')}<br>"
            corpo += f"<b>Categorias:</b> {', '.join(ip_info.get('categorias_reportadas', []))}<br>"
            corpo += f"<b>Data Verificação:</b> {ip_info.get('data_verificacao', 'N/A')}<br>"
            if ip_info.get('comentarios_recentes'):
                corpo += "<b>Comentários Recentes:</b><ul>"
                for comentario in ip_info['comentarios_recentes']:
                    corpo += f"<li>{comentario}</li>"
                corpo += "</ul>"
            corpo += "</li><br>"

        corpo += """
            </ul>
            <p>Este é um relatório automático gerado pelo sistema de monitoramento.</p>
            <p>Atenciosamente,</p>
            <p>Equipe de Monitoramento de Segurança</p>
        </body>
        </html>
        """
        return corpo

    def executar(self):
        logger.info("--- Iniciando Análise Otimizada de IPs da Locaweb ---")
        historico_locaweb = self._carregar_historico()
        logger.info(f"{len(historico_locaweb)} IPs da Locaweb no histórico.")

        ips_locaweb_na_blocklist = self.baixar_e_filtrar_blocklist()

        if not ips_locaweb_na_blocklist:
            logger.info("Nenhum IP da Locaweb encontrado na blocklist hoje.")
            self._salvar_json(self.arquivo_diario, [])
            self._salvar_json(self.arquivo_diario_kinghost, []) # Garante que o arquivo KingHost seja limpo
            return

        # Instancia o verificador do AbuseIPDB uma vez
        
        verificador_abuso = AbuseIPDBChecker()

        relatorio_diario_completo = [] # Todos os IPs que serão adicionados ao histórico
        relatorio_diario_kinghost = []
        relatorio_diario_locaweb_outros = []

        total_para_checar = len(ips_locaweb_na_blocklist)
        for i, info_base in enumerate(ips_locaweb_na_blocklist):
            ip = info_base['ip']
            logger.debug(f"Processando IP {i+1}/{total_para_checar}: {ip}")
            
            deve_reportar = False
            if ip not in historico_locaweb:
                logger.info(f"IP NOVO da Locaweb encontrado: {ip}")
                deve_reportar = True
            else:
                data_anterior = datetime.strptime(historico_locaweb[ip]['data_verificacao'], "%d/%m/%Y")
                if self.hoje - data_anterior > timedelta(days=30):
                    logger.info(f"IP ANTIGO da Locaweb (visto há mais de 30 dias): {ip}")
                    deve_reportar = True
                else:
                    logger.debug(f"IP RECENTE da Locaweb (ignorado): {ip}")

            if deve_reportar:
                time.sleep(1) # Pausa para não sobrecarregar as APIs
                hostname = self.obter_hostname(ip)
                info_abuso = verificador_abuso.verificar_ip(ip)
                
                # Monta o registro completo
                registro_completo = info_base.copy()
                registro_completo['hostname'] = hostname
                registro_completo['data_verificacao'] = self.hoje.strftime("%d/%m/%Y") # Formato brasileiro
                # Adiciona os dados do AbuseIPDB
                registro_completo.update(info_abuso)
                
                relatorio_diario_completo.append(registro_completo)
                historico_locaweb[ip] = registro_completo

                # Separa para os relatórios diários específicos
                if re.search(r"kinghost", registro_completo.get('hostname', ''), re.IGNORECASE):
                    relatorio_diario_kinghost.append(registro_completo)
                else:
                    relatorio_diario_locaweb_outros.append(registro_completo)

        self._salvar_json(self.arquivo_diario_kinghost, relatorio_diario_kinghost)
        self._salvar_json(self.arquivo_diario, relatorio_diario_locaweb_outros)

        self._salvar_json(self.arquivo_historico, list(historico_locaweb.values()))
        logger.info("--- Análise Otimizada Concluída ---")

        # Envio de e-mail de notificação
        if relatorio_diario_kinghost:
            try:
                notificador = NotificadorEmail()
                assunto = f"Novos IPs da KingHost Reportados no AbuseIPDB - {self.hoje.strftime("%d/%m/%Y")}"
                corpo_email_html = self._construir_corpo_email_notificacao(relatorio_diario_kinghost, "KingHost")
                notificador.enviar_email(assunto, corpo_email_html, anexo_path=self.arquivo_diario_kinghost)
            except Exception:
                logger.error("Falha ao enviar e-mail da KingHost.", exc_info=True)
        
        if relatorio_diario_locaweb_outros:
            try:
                notificador = NotificadorEmail()
                assunto = f"Novos IPs da Locaweb Reportados no AbuseIPDB - {self.hoje.strftime("%d/%m/%Y")}"
                corpo_email_html = self._construir_corpo_email_notificacao(relatorio_diario_locaweb_outros, "Locaweb")
                notificador.enviar_email(assunto, corpo_email_html, anexo_path=self.arquivo_diario)
            except Exception:
                logger.error("Falha ao enviar e-mail da Locaweb (outros).", exc_info=True)
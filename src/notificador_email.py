# -*- coding: utf-8 -*-

import logging
import os
import smtplib
import ssl  # For secure context
from email.message import EmailMessage  # Modern way to construct emails
from email.mime.application import MIMEApplication  # For attachments

from dotenv import load_dotenv

# Carrega as variáveis do .env para o ambiente (garante que estejam disponíveis)
load_dotenv()

logger = logging.getLogger(__name__)


class NotificadorEmail:
    """
    Classe responsável por enviar notificações por e-mail, com suporte a anexos
    e práticas de segurança modernas.
    """

    def __init__(self):
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))  # Default para 587
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.receiver_email = os.getenv("EMAIL_RECEIVER")

        # Contexto SSL seguro
        self.context = ssl.create_default_context()

        # Validação básica das configurações
        if not all(
            [
                self.smtp_server,
                self.sender_email,
                self.sender_password,
                self.receiver_email,
            ]
        ):
            logger.critical("Configurações de e-mail incompletas no arquivo .env!")
            raise ValueError(
                "Configurações de e-mail (servidor, remetente, senha, destinatário) são obrigatórias."
            )

    def enviar_email(self, assunto, corpo_html, anexo_path=None):
        """
        Envia um e-mail com o assunto, corpo HTML e, opcionalmente, um anexo.
        """
        msg = EmailMessage()
        msg["Subject"] = assunto
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email
        msg.set_content(corpo_html, subtype="html")  # Define o corpo como HTML

        if anexo_path:
            try:
                with open(anexo_path, "rb") as f:
                    file_data = f.read()

                # Adiciona o anexo
                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=os.path.basename(anexo_path),
                )
                logger.info(
                    f"Anexo '{os.path.basename(anexo_path)}' adicionado ao e-mail."
                )
            except FileNotFoundError:
                logger.error(
                    f"Arquivo de anexo não encontrado: {anexo_path}", exc_info=True
                )
            except Exception:
                logger.error(f"Erro ao adicionar anexo: {anexo_path}", exc_info=True)

        logger.info(
            f"Tentando conectar ao servidor SMTP: {self.smtp_server}:{self.smtp_port}"
        )
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=self.context)  # Inicia TLS
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            logger.info(
                f"E-mail enviado com sucesso para {self.receiver_email} com o assunto: {assunto}"
            )
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "Falha na autenticação SMTP. Verifique usuário e senha.", exc_info=True
            )
            raise
        except smtplib.SMTPConnectError:
            logger.error(
                "Falha na conexão SMTP. Verifique o servidor e a porta.", exc_info=True
            )
            raise
        except Exception:
            logger.error(f"Erro inesperado ao enviar e-mail.", exc_info=True)
            raise

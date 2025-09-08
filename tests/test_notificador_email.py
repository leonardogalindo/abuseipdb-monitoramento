
import pytest
import smtplib
from src.notificador_email import NotificadorEmail

@pytest.fixture
def mock_env(mocker):
    """Mocks environment variables for email settings."""
    return mocker.patch('os.getenv', side_effect=lambda key, default=None: {
        "EMAIL_SMTP_SERVER": "smtp.fake.com",
        "EMAIL_SMTP_PORT": "587",
        "EMAIL_SENDER": "sender@fake.com",
        "EMAIL_PASSWORD": "fakepassword",
        "EMAIL_RECEIVER": "receiver@fake.com",
    }.get(key, default))

@pytest.fixture
def mock_smtp(mocker):
    """Mocks smtplib.SMTP for use in a 'with' statement."""
    # Mock a classe SMTP
    smtp_class_mock = mocker.patch('smtplib.SMTP', autospec=True)
    # O 'with' statement chama __enter__ no objeto da classe, então mocamos isso
    smtp_instance_mock = smtp_class_mock.return_value.__enter__.return_value
    return smtp_instance_mock

@pytest.fixture
def mock_ssl_context(mocker):
    """Mocks ssl.create_default_context."""
    return mocker.patch('ssl.create_default_context', autospec=True)

def test_notificador_init_success(mock_env, mock_ssl_context):
    notificador = NotificadorEmail()
    assert notificador.smtp_server == "smtp.fake.com"

def test_notificador_init_missing_config(mock_env):
    mock_env.side_effect = lambda key, default=None: default if key == 'EMAIL_SMTP_PORT' else None
    with pytest.raises(ValueError, match="Configurações de e-mail .* obrigatórias"):
        NotificadorEmail()

def test_enviar_email_sucesso(mock_env, mock_smtp, mock_ssl_context):
    notificador = NotificadorEmail()
    notificador.enviar_email("Assunto", "<p>Corpo</p>")

    # Verifica as chamadas na instância retornada pelo 'with'
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once_with("sender@fake.com", "fakepassword")
    mock_smtp.send_message.assert_called_once()

def test_enviar_email_falha_autenticacao(mock_env, mock_smtp, mock_ssl_context):
    notificador = NotificadorEmail()
    mock_smtp.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Auth failed')

    with pytest.raises(smtplib.SMTPAuthenticationError):
        notificador.enviar_email("Assunto", "<p>Corpo</p>")

    mock_smtp.send_message.assert_not_called()

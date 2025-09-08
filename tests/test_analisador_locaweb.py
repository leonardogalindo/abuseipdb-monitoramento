
import pytest
from src.analisador_locaweb import AnalisadorLocaweb

# --- Mocks Fixtures ---

@pytest.fixture
def mock_notificador(mocker):
    """Mocks the NotificadorEmail class."""
    return mocker.patch('src.analisador_locaweb.NotificadorEmail', autospec=True).return_value

@pytest.fixture
def mock_abuse_checker(mocker):
    """Mocks the AbuseIPDBChecker class where it's imported."""
    # O import está dentro do método executar, então o patch deve ter o mesmo alvo
    mock = mocker.patch('src.analisador_locaweb.AbuseIPDBChecker', autospec=True)
    instance = mock.return_value
    instance.verificar_ip.return_value = {
        'abuseConfidenceScore': 90,
        'categorias_reportadas': ['Spam'],
        'comentarios_recentes': ['Email spam activity']
    }
    return instance

@pytest.fixture
def mock_requests_session(mocker):
    """Mocks requests.Session and its get calls."""
    mock_session_class = mocker.patch('requests.Session', autospec=True)
    mock_session_instance = mock_session_class.return_value
    mock_session_instance.headers = {}

    # Mock para a resposta da blocklist
    mock_blocklist_response = mocker.Mock()
    mock_blocklist_response.text = '187.45.198.12    AS27699    Locaweb Servicos de Internet S/A'
    mock_blocklist_response.raise_for_status.return_value = None

    # Mock para a resposta da API de hostname
    mock_hostname_response = mocker.Mock()
    mock_hostname_response.json.return_value = {"status": "success", "reverse": "mail.kinghost.net"}
    mock_hostname_response.raise_for_status.return_value = None

    # A primeira chamada a get() retorna a blocklist, a segunda o hostname
    mock_session_instance.get.side_effect = [mock_blocklist_response, mock_hostname_response]
    return mock_session_instance

@pytest.fixture
def mock_fs(mocker):
    """Mocks filesystem operations."""
    mocker.patch('os.path.exists', return_value=False) # Simula histórico vazio
    return mocker.patch('builtins.open', mocker.mock_open())

# --- Test Cases ---

def test_executar_com_ip_novo(mock_fs, mock_requests_session, mock_abuse_checker, mock_notificador):
    """
    Tests the main execution flow when a new IP is found.
    """
    analisador = AnalisadorLocaweb(
        url_blocklist='http://fake-blocklist.com',
        arquivo_historico='data/fake_historico.json',
        arquivo_diario='data/fake_diario.json',
        arquivo_diario_kinghost='data/fake_diario_kinghost.json'
    )

    analisador.executar()

    # 1. Verifica chamadas de API
    mock_requests_session.get.assert_any_call('http://fake-blocklist.com')
    mock_requests_session.get.assert_any_call('http://ip-api.com/json/187.45.198.12?fields=status,message,reverse')
    mock_abuse_checker.verificar_ip.assert_called_once_with('187.45.198.12')

    # 2. Verifica envio de e-mail
    mock_notificador.enviar_email.assert_called_once()
    args, _ = mock_notificador.enviar_email.call_args
    assert "Novos IPs da KingHost Reportados" in args[0]
    assert "<li><b>IP:</b> 187.45.198.12<br>" in args[1]

    # 3. Verifica escrita de arquivos
    assert mock_fs().write.call_count >= 3 # Pelo menos 3 escritas (diario, diario_kinghost, historico)

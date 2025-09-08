import pytest
import requests
from src.abuseipdb_checker import AbuseIPDBChecker

@pytest.fixture
def mock_env(mocker):
    """Mocks os.getenv for the API key."""
    return mocker.patch('os.getenv', return_value='fake_api_key')

@pytest.fixture
def mock_requests_get(mocker):
    """Mocks the requests.get call."""
    return mocker.patch('requests.get')

def test_checker_init_success(mock_env):
    """Tests successful initialization."""
    checker = AbuseIPDBChecker()
    assert checker.api_key == 'fake_api_key'
    # Verifica a URL hardcoded
    assert checker.base_url == "https://api.abuseipdb.com/api/v2/reports"

def test_checker_init_missing_key(mocker):
    """Tests that ValueError is raised if API key is missing."""
    mocker.patch('os.getenv', return_value=None)
    with pytest.raises(ValueError, match="Chave da API não configurada"):
        AbuseIPDBChecker()

def test_verificar_ip_sucesso(mock_env, mock_requests_get):
    """Tests a successful IP check with reports."""
    checker = AbuseIPDBChecker()
    
    # Mock da resposta da API
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "results": [
                {
                    "comment": "SSH brute-force",
                    "categories": [22],
                    "reportedAt": "2025-09-01T10:00:00+00:00"
                },
                {
                    "comment": "Bad web bot",
                    "categories": [19],
                    "reportedAt": "2025-09-01T11:00:00+00:00"
                }
            ]
        }
    }

    result = checker.verificar_ip('1.2.3.4')

    # Asserções
    assert result['categorias_reportadas'] == ['Bad Web Bot', 'SSH']
    assert len(result['comentarios_recentes']) == 2
    assert "[01/09/2025 10:00:00] SSH brute-force" in result['comentarios_recentes']

def test_verificar_ip_sem_relatorios(mock_env, mock_requests_get):
    """Tests an IP check that returns no reports."""
    checker = AbuseIPDBChecker()
    mock_response = mock_requests_get.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": {"results": []}}

    result = checker.verificar_ip('1.2.3.4')
    assert result == {"categorias_reportadas": [], "comentarios_recentes": []}

def test_verificar_ip_erro_api(mock_env, mock_requests_get):
    """Tests handling of a non-200 API response."""
    checker = AbuseIPDBChecker()
    mock_requests_get.return_value.raise_for_status.side_effect = requests.HTTPError

    result = checker.verificar_ip('1.2.3.4')
    expected_error = {
        "categorias_reportadas": ["Erro na consulta"],
        "comentarios_recentes": [],
    }
    assert result == expected_error
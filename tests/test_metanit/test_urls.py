import requests
from requests.exceptions import RequestException
import pytest


@pytest.mark.parametrize("endpoint", [
    '/',
    'content/',
    'recommendations/',
    'accounts/login/',
    'accounts/signup/',
])
def test_endpoints(test_url: str, endpoint: str) -> None:
    url = test_url + endpoint
    try:
        response = requests.get(url)
        assert response.status_code == 200
    except RequestException as e:
        assert False, f"Request failed: {e}"


@pytest.mark.django_db
def test_url_id_content(test_url: str, test_content_id: list) -> None:
    for content_id in test_content_id:
        url = f"{test_url}content/{content_id}/"
        try:
            response = requests.get(url)
            assert response.status_code == 200
        except RequestException as e:
            assert False, f"Request failed for content {content_id}: {e}"

import pytest
from application.models import Content


@pytest.fixture(scope='function')
def test_url(request: None) -> str:
    return 'http://127.0.0.1:8000/'


@pytest.fixture(scope='function')
def test_content_id(db) -> list:
    return [str(content.id) for content in Content.objects.all()]

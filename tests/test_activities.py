import pytest
from fastapi.testclient import TestClient
import src.app as appmod


@pytest.fixture
def client():
    return TestClient(appmod.app)


def test_get_activities(client):
    r = client.get('/activities')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # expect some known activities from seed data
    assert 'Chess Club' in data


def test_signup_and_duplicate(client):
    email = 'pytest_user@example.com'
    # ensure clean state: try removing if present
    client.delete(f"/activities/Chess%20Club/participants?email={email}")

    # signup should succeed
    r = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r.status_code == 200
    assert 'Signed up' in r.json().get('message', '')

    # duplicate signup should return 400
    r2 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r2.status_code == 400
    assert 'already' in r2.json().get('detail', '').lower()

    # cleanup
    client.delete(f"/activities/Chess%20Club/participants?email={email}")


def test_unregister_behaviour(client):
    email = 'to_remove@example.com'
    # ensure present
    client.post(f"/activities/Chess%20Club/signup?email={email}")

    # remove
    r = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert r.status_code == 200
    assert 'Unregistered' in r.json().get('message', '')

    # removing again should 404
    r2 = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert r2.status_code == 404

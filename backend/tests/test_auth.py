from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoints():
    assert client.get('/health').status_code == 200
    assert client.get('/ready').status_code == 200


def test_login_returns_tokens_for_seed_admin():
    resp = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert 'access_token' in body
    assert 'refresh_token' in body
    assert body['token_type'] == 'bearer'


def test_current_user_endpoint_works():
    login = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    token = login.json()['access_token']
    resp = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body['email'] == 'admin@docuforge.ai'
    assert body['role_name'] == 'super_admin'


def test_refresh_rotates_tokens():
    login = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    refresh_token = login.json()['refresh_token']
    resp = client.post('/api/v1/auth/refresh', json={'refresh_token': refresh_token})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body['refresh_token'] != refresh_token
    assert body['access_token']


def test_logout_revokes_session_tokens():
    login = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    access_token = login.json()['access_token']
    refresh_token = login.json()['refresh_token']
    logout = client.post('/api/v1/auth/logout', json={'refresh_token': refresh_token}, headers={'Authorization': f'Bearer {access_token}'})
    assert logout.status_code == 200, logout.text
    me = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {access_token}'})
    assert me.status_code == 401


def test_protected_route_requires_authentication():
    resp = client.get('/api/v1/users')
    assert resp.status_code == 401


def test_admin_token_can_access_users():
    login = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    token = login.json()['access_token']
    resp = client.get('/api/v1/users', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.json()
    assert any(item['email'] == 'admin@docuforge.ai' for item in data)


def test_department_duplicate_name_returns_conflict():
    login = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    token = login.json()['access_token']
    payload = {'name': 'Platform Engineering Test', 'code': 'PLATTEST', 'description': 'Conflict check'}
    first = client.post('/api/v1/departments', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert first.status_code == 200, first.text
    second = client.post('/api/v1/departments', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert second.status_code == 409, second.text


def test_template_duplicate_code_returns_conflict():
    login = client.post('/api/v1/auth/login', json={'email': 'admin@docuforge.ai', 'password': 'DocuForgeAdmin2026!'})
    token = login.json()['access_token']
    payload = {'name': 'Duplicate Template Check', 'code': 'DUP-TEMPLATE-001', 'description': 'Conflict check'}
    first = client.post('/api/v1/templates', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert first.status_code == 200, first.text
    second = client.post('/api/v1/templates', json=payload, headers={'Authorization': f'Bearer {token}'})
    assert second.status_code == 409, second.text

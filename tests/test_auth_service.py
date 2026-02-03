from services.auth_service import AuthService
from infrastructure.database.models import User


def test_auth_token_includes_role():
    service = AuthService(secret="test-secret", expire_hours=1)
    user = User(name="tester", email="tester@example.com", password="hashed", role="admin")
    token = service._create_token(user)
    payload = service.verify_token(token)

    assert payload["role"] == "admin"


def test_password_hash_roundtrip():
    service = AuthService(secret="test-secret", expire_hours=1)
    hashed = service.hash_password("password123")
    assert service.verify_password("password123", hashed)

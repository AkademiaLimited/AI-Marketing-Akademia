from app.models.user import User
from app.schemas.user import UserOut


def test_user_response_accepts_local_development_email():
    user = User(
        id="admin@akademia.local",
        email="admin@akademia.local",
        name="Admin",
        hashed_password="hash",
        is_active=True,
        is_superuser=True,
    )

    response = UserOut.model_validate(user)

    assert response.email == "admin@akademia.local"
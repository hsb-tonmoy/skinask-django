import pytest
from django.http.request import HttpHeaders
from ninja_extra.testing import TestClient
from ninja_jwt.tokens import RefreshToken

# You'll need to import your controllers
from users.api import UserController  # Adjust this import path as needed
from users.models import CustomUser


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="test@example.com",
        password="tacerLinDesTIPAL",
        first_name="Test",
        last_name="User",
        language="en",
        timezone="UTC",
    )


@pytest.fixture
def client():
    client = TestClient(UserController)
    return client


@pytest.fixture
def refresh(user):
    return RefreshToken.for_user(user)


@pytest.mark.django_db
class TestUsersController:
    def test_get_current_user(self, client, refresh, user):
        """Test retrieving the current user's profile."""
        response = client.get("/me", headers={"Authorization": f"Bearer {refresh.access_token}"})

        print(response.json())

        assert response.status_code == 200
        assert response.json()["email"] == user.email
        assert response.json()["first_name"] == user.first_name
        assert response.json()["last_name"] == user.last_name
        assert response.json()["language"] == user.language
        assert response.json()["timezone"] == user.timezone

    def test_update_profile(self, client, refresh, user):
        """Test updating the user's profile."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "language": "en",
            "timezone": "America/New_York",
        }

        response = client.patch(
            "/me", json=data, headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Refresh user from database
        user.refresh_from_db()

        # Check that fields were updated
        assert user.first_name == "Updated"
        assert user.last_name == "Name"
        assert user.timezone == "America/New_York"

    def test_update_language(self, client, refresh, user):
        """Test updating the user's language preference."""
        data = {"language": "bn"}

        response = client.patch(
            "/me", json=data, headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["user"]["language"] == "bn"

        # Refresh user from database
        user.refresh_from_db()

        # Check that language was updated
        assert user.language == "bn"

    def test_update_profile_invalid_language(self, client, refresh, user):
        """Test updating the profile with an invalid language."""
        data = {"language": "invalid"}

        response = client.patch(
            "/me", json=data, headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        # Should return a validation error
        assert response.status_code == 422

    def test_update_profile_unauthenticated(self, client, user):
        """Test that unauthenticated users cannot update profiles."""
        # Create client without authentication
        data = {"first_name": "Unauthorized"}

        response = client.patch("/me", json=data)

        # Should return unauthorized
        assert response.status_code == 401

    def test_partial_update(self, client, refresh, user):
        """Test that partial updates work correctly."""
        # Update only first_name
        data = {"first_name": "Partial"}
        response = client.patch(
            "/me", json=data, headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        assert response.status_code == 200

        # Refresh user from database
        user.refresh_from_db()

        # Check that only first_name was updated
        assert user.first_name == "Partial"
        assert user.last_name == "User"  # Unchanged
        assert user.language == "en"  # Unchanged
        assert user.timezone == "UTC"  # Unchanged

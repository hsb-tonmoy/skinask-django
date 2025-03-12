from django.test import TransactionTestCase
from django.urls import reverse
from ninja_jwt.tokens import RefreshToken
from rest_framework.test import APIClient

from users.models import CustomUser


class UserAPITestCase(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
            language="en",
            timezone="UTC",
        )

        # Get JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_current_user(self):
        """Test retrieving the current user's profile."""
        url = reverse("api-1.0.0:users_controller_get_current_user")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)
        self.assertEqual(response.data["last_name"], self.user.last_name)
        self.assertEqual(response.data["language"], self.user.language)
        self.assertEqual(response.data["timezone"], self.user.timezone)

    def test_update_profile(self):
        """Test updating the user's profile."""
        url = reverse("api-1.0.0:users_controller_update_profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "language": "en",
            "timezone": "America/New_York",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["success"], True)

        # Refresh user from database
        self.user.refresh_from_db()

        # Check that fields were updated
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.timezone, "America/New_York")

    def test_update_language(self):
        """Test updating the user's language preference."""
        url = reverse("api-1.0.0:users_controller_update_language")
        data = {"language": "bn"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["success"], True)
        self.assertEqual(response.data["language"], "bn")

        # Refresh user from database
        self.user.refresh_from_db()

        # Check that language was updated
        self.assertEqual(self.user.language, "bn")

    def test_update_profile_invalid_language(self):
        """Test updating the profile with an invalid language."""
        url = reverse("api-1.0.0:users_controller_update_profile")
        data = {"language": "invalid"}

        response = self.client.patch(url, data, format="json")

        # Should return a validation error
        self.assertEqual(response.status_code, 422)

    def test_update_profile_unauthenticated(self):
        """Test that unauthenticated users cannot update profiles."""
        # Remove authentication
        self.client.credentials()

        url = reverse("api-1.0.0:users_controller_update_profile")
        data = {"first_name": "Unauthorized"}

        response = self.client.patch(url, data, format="json")

        # Should return unauthorized
        self.assertEqual(response.status_code, 401)

    def test_partial_update(self):
        """Test that partial updates work correctly."""
        url = reverse("api-1.0.0:users_controller_update_profile")

        # Update only first_name
        data = {"first_name": "Partial"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, 200)

        # Refresh user from database
        self.user.refresh_from_db()

        # Check that only first_name was updated
        self.assertEqual(self.user.first_name, "Partial")
        self.assertEqual(self.user.last_name, "User")  # Unchanged
        self.assertEqual(self.user.language, "en")  # Unchanged
        self.assertEqual(self.user.timezone, "UTC")  # Unchanged

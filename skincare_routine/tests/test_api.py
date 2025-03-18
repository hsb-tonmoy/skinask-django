import pytest
from django.core.cache import cache
from ninja_extra.testing import TestClient
from ninja_jwt.tokens import RefreshToken

from skincare_routine.api import SkincareRoutinesController
from skincare_routine.models import (
    RoutineStep,
    SkincareRoutine,
    SkincareRoutinePeriod,
    SkincareRoutineProductType,
)
from users.models import CustomUser


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="test@example.com",
        password="testPassword123",
        first_name="Test",
        last_name="User",
        language="en",
        timezone="UTC",
    )


@pytest.fixture
def client():
    client = TestClient(SkincareRoutinesController)
    return client


@pytest.fixture
def refresh(user):
    return RefreshToken.for_user(user)


@pytest.fixture
def product_type():
    return SkincareRoutineProductType.objects.create(name="Cleanser")


@pytest.fixture
def period():
    return SkincareRoutinePeriod.objects.create(name="Morning")


@pytest.fixture
def skincare_routine(user):
    return SkincareRoutine.objects.create(
        title="Test Routine",
        description="Test Description",
        created_by=user,
    )


@pytest.fixture
def routine_step(skincare_routine, product_type, period):
    return RoutineStep.objects.create(
        routine=skincare_routine,
        product_type=product_type,
        period=period,
        day_of_week="mon",
        product_name="Test Product",
        sort_order=1,
    )


@pytest.mark.django_db
class TestSkincareRoutinesController:
    def test_list_routines(self, client, refresh, user, skincare_routine):
        """Test listing all routines for the current user."""
        # Clear cache to ensure fresh data
        cache.clear()

        response = client.get("", headers={"Authorization": f"Bearer {refresh.access_token}"})

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == skincare_routine.id
        assert response.json()[0]["title"] == skincare_routine.title
        assert response.json()[0]["description"] == skincare_routine.description

    def test_list_routines_creates_default(self, client, refresh, user):
        """Test that listing routines creates a default routine if none exists."""
        # Clear cache to ensure fresh data
        cache.clear()

        response = client.get("", headers={"Authorization": f"Bearer {refresh.access_token}"})

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "My Skincare Routine"
        assert response.json()[0]["description"] == "My personalized skincare routine"

    def test_get_routine_options(self, client, refresh, product_type, period):
        """Test retrieving routine options."""
        # Clear cache to ensure fresh data
        cache.clear()

        response = client.get(
            "/options", headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        assert response.status_code == 200
        assert "product_types" in response.json()
        assert "periods" in response.json()
        assert "days_of_week" in response.json()

        # Check that our fixtures are in the response
        product_types = response.json()["product_types"]
        periods = response.json()["periods"]

        assert any(
            pt["value"] == product_type.id and pt["label"] == product_type.name
            for pt in product_types
        )
        assert any(p["value"] == period.id and p["label"] == period.name for p in periods)

    def test_create_routine_steps(self, client, refresh, skincare_routine, product_type, period):
        """Test creating routine steps."""
        # Clear cache to ensure fresh data
        cache.clear()

        data = {
            "skincare_routine": skincare_routine.id,
            "days_of_week": ["mon", "wed", "fri"],
            "product": {"value": 0, "label": "Test Product"},
            "product_type": product_type.id,
            "period": period.id,
            "color": "#FF5733",
            "notes": "Test notes",
            "reminders": {},
        }

        response = client.post(
            "/steps", json=data, headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        assert response.status_code == 200

        [response_data] = response.json()

        assert response_data["product_name"] == "Test Product"
        assert response_data["product_type"] == product_type.id
        assert response_data["period"] == period.id
        assert response_data["color"] == "#FF5733"
        assert response_data["notes"] == "Test notes"

        # Check that steps were created for each day
        routine_steps = RoutineStep.objects.filter(routine=skincare_routine)
        assert routine_steps.count() == 3

        # Check days of week
        days = [step.day_of_week for step in routine_steps]
        assert set(days) == set(["mon", "wed", "fri"])

    def test_update_routine_step(self, client, refresh, routine_step):
        """Test updating a routine step."""
        # Clear cache to ensure fresh data
        cache.clear()

        data = {"color": "#00FF00", "notes": "Updated notes"}

        response = client.patch(
            f"/steps/{routine_step.id}",
            json=data,
            headers={"Authorization": f"Bearer {refresh.access_token}"},
        )

        assert response.status_code == 200

        # Refresh from database
        routine_step.refresh_from_db()

        # Check that fields were updated
        assert routine_step.color == "#00FF00"
        assert routine_step.notes == "Updated notes"

    def test_delete_routine_step(self, client, refresh, routine_step):
        """Test deleting a routine step."""
        # Clear cache to ensure fresh data
        cache.clear()

        response = client.delete(
            f"/steps/{routine_step.id}", headers={"Authorization": f"Bearer {refresh.access_token}"}
        )

        assert response.status_code == 200

        # Check that step was deleted
        with pytest.raises(RoutineStep.DoesNotExist):
            RoutineStep.objects.get(id=routine_step.id)

    def test_unauthorized_access(self, client):
        """Test that unauthenticated users cannot access endpoints."""
        # Try to access endpoints without authentication
        list_response = client.get("")
        options_response = client.get("/options")
        create_response = client.post("/steps", json={})
        update_response = client.patch("/steps/1", json={})
        delete_response = client.delete("/steps/1")

        # All should return 401 Unauthorized
        assert list_response.status_code == 401
        assert options_response.status_code == 401
        assert create_response.status_code == 401
        assert update_response.status_code == 401
        assert delete_response.status_code == 401

    def test_permission_denied(self, client, refresh, routine_step):
        """Test that users cannot modify other users' routine steps."""
        # Create another user
        other_user = CustomUser.objects.create_user(
            email="other@example.com",
            password="otherPassword123",
            first_name="Other",
            last_name="User",
        )
        other_refresh = RefreshToken.for_user(other_user)

        # Try to update and delete with other user's token
        update_response = client.patch(
            f"/steps/{routine_step.id}",
            json={"notes": "Unauthorized update"},
            headers={"Authorization": f"Bearer {other_refresh.access_token}"},
        )

        delete_response = client.delete(
            f"/steps/{routine_step.id}",
            headers={"Authorization": f"Bearer {other_refresh.access_token}"},
        )

        # Should return 403 Permission Denied
        assert update_response.status_code == 403
        assert delete_response.status_code == 403

        # Verify step was not modified
        routine_step.refresh_from_db()
        assert routine_step.notes != "Unauthorized update"

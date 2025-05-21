from main.models import CV, Skill, Project
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    """Fixture to provide an API client instance."""
    return APIClient()


@pytest.fixture
def skill_python():
    """Fixture to create and return a Skill object named 'Python'."""
    return Skill.objects.create(name="Python")


@pytest.fixture
def skill_django():
    """Fixture to create and return a Skill object named 'Django'."""
    return Skill.objects.create(name="Django")


@pytest.fixture
def cv1_fixture(skill_python, skill_django):
    """
    Fixture to create and return a CV object for John Doe,
    associated with Python and Django skills, and Project Alpha.
    """
    cv = CV.objects.create(
        firstname="John",
        lastname="Doe",
        bio="Developer from Testland.",
        contacts={
            "email": "john.doe@example.com",
            "linkedin": "linkedin.com/johndoe"
        }
    )
    cv.skills.add(skill_python, skill_django)
    Project.objects.create(
        cv=cv,
        name="Project Alpha",
        description="First test project."
    )
    return cv


@pytest.fixture
def cv2_fixture(skill_python):
    """
    Fixture to create and return a CV object for Jane Smith,
    associated with Python skill and Project Beta.
    """
    cv = CV.objects.create(
        firstname="Jane",
        lastname="Smith",
        bio="Another developer.",
        contacts={"github": "github.com/janesmith"}
    )
    cv.skills.add(skill_python)
    Project.objects.create(
        cv=cv,
        name="Project Beta",
        description="Second test project."
    )
    return cv


@pytest.fixture
def cv_payload_valid_fixture(skill_python, skill_django):
    """Fixture for a valid CV creation payload."""
    return {
        "firstname": "Alice",
        "lastname": "Wonderland",
        "bio": "Curiouser and curiouser.",
        "contacts": {"email": "alice@example.com"},
        "skills": [skill_python.id, skill_django.id],
        "projects": [
            {
                "name": "Tea Party Project",
                "description": "Organizing a mad tea party."
            }
        ]
    }

@pytest.fixture
def cv_payload_update_fixture(skill_python):
    """Fixture for a valid CV update payload."""
    return {
        "firstname": "John",
        "lastname": "Doer",
        "bio": "An updated bio for John.",
        "contacts": {"email": "john.doer@example.com", "phone": "987654321"},
        "skills": [skill_python.id],
        "projects": [
            {
                "name": "Project Gamma",
                "description": "A new project.",
                "link": "http://gamma.com"
            }
        ]
    }


class TestCVAPI:
    def test_api_create_cv(
            self, api_client, cv_payload_valid_fixture,
            skill_python, skill_django
        ):
        """Test creating a new CV via API."""
        url = reverse('main:cv-api-list')
        response = api_client.post(
            url, cv_payload_valid_fixture, format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert CV.objects.count() == 1
        created_cv = CV.objects.get(firstname="Alice")
        assert created_cv.lastname == "Wonderland"
        assert skill_python in created_cv.skills.all()
        assert skill_django in created_cv.skills.all()
        assert created_cv.projects.count() == 1
        assert created_cv.projects.first().name == "Tea Party Project"
        assert response.data['contacts']['email'] == "alice@example.com"

    def test_api_list_cvs(self, api_client, cv1_fixture, cv2_fixture):
        """Test listing CVs via API."""
        url = reverse('main:cv-api-list')
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        response_cv_firstnames = sorted(
            [item['firstname'] for item in response.data]
        )
        expected_firstnames = sorted(
            [cv1_fixture.firstname, cv2_fixture.firstname]
        )
        assert response_cv_firstnames == expected_firstnames
        if len(response.data) > 0:
            assert 'projects' in response.data[0]
            assert 'skills' in response.data[0]

    def test_api_retrieve_cv(
            self, api_client, cv1_fixture, skill_python, skill_django
        ):
        """Test retrieving a single CV via API."""
        url = reverse('main:cv-api-detail', kwargs={'pk': cv1_fixture.pk})
        response = api_client.get(url, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == cv1_fixture.pk
        assert response.data['firstname'] == cv1_fixture.firstname
        assert response.data['lastname'] == cv1_fixture.lastname
        assert response.data['bio'] == cv1_fixture.bio
        assert set(response.data['skills']) == {
            skill_python.id, skill_django.id
        }
        assert len(response.data['projects']) == 1
        assert response.data['projects'][0]['name'] == "Project Alpha"
        assert response.data['contacts']['email'] == cv1_fixture.contacts['email']

    def test_api_update_cv(
            self, api_client, cv1_fixture,
            cv_payload_update_fixture, skill_python
        ):
        """Test updating a CV via API (PUT)."""
        url = reverse('main:cv-api-detail', kwargs={'pk': cv1_fixture.pk})
        response = api_client.put(
            url, cv_payload_update_fixture, format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        cv1_fixture.refresh_from_db()
        assert cv1_fixture.lastname == "Doer"
        assert cv1_fixture.bio == "An updated bio for John."
        assert skill_python in cv1_fixture.skills.all()
        assert cv1_fixture.skills.count() == 1
        assert cv1_fixture.projects.count() == 1
        assert cv1_fixture.projects.first().name == "Project Gamma"
        assert cv1_fixture.contacts['phone'] == "987654321"

    def test_api_partial_update_cv(
            self, api_client, cv1_fixture, skill_django
        ):
        """Test partially updating a CV via API (PATCH)."""
        url = reverse('main:cv-api-detail', kwargs={'pk': cv1_fixture.pk})
        patch_data = {
            "bio": "A very specific new bio.",
            "skills": [skill_django.id]
        }
        response = api_client.patch(url, patch_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        cv1_fixture.refresh_from_db()
        assert cv1_fixture.firstname == "John"
        assert cv1_fixture.bio == "A very specific new bio."
        assert skill_django in cv1_fixture.skills.all()
        assert cv1_fixture.skills.count() == 1
        assert cv1_fixture.projects.first().name == "Project Alpha"

    def test_api_delete_cv(self, api_client, cv1_fixture):
        """Test deleting a CV via API."""
        assert CV.objects.filter(pk=cv1_fixture.pk).exists()
        initial_cv_count = CV.objects.count()

        url = reverse('main:cv-api-detail', kwargs={'pk': cv1_fixture.pk})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CV.objects.count() == initial_cv_count - 1
        with pytest.raises(CV.DoesNotExist):
            CV.objects.get(pk=cv1_fixture.pk)

    def test_api_create_cv_invalid_payload(self, api_client):
        """
        Test creating a CV with invalid data (e.g., missing required field).
        """
        url = reverse('main:cv-api-list')
        invalid_payload = {
            "lastname": "MissingFirstname",
            "bio": "Test bio"
        }
        response = api_client.post(url, invalid_payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'firstname' in response.data

    def test_api_retrieve_non_existent_cv(self, api_client):
        """Test retrieving a non-existent CV returns 404."""
        non_existent_pk = 99999
        while CV.objects.filter(pk=non_existent_pk).exists():
            non_existent_pk +=1

        url = reverse('main:cv-api-detail', kwargs={'pk': non_existent_pk})
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

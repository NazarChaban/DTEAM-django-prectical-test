from main.models import CV, Skill, Project
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def skill_python():
    return Skill.objects.create(name="Python")


@pytest.fixture
def skill_django():
    return Skill.objects.create(name="Django")


@pytest.fixture
def cv1(skill_python, skill_django):
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
def cv2(skill_python):
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


def test_cv_list_view_status_code(client):
    response = client.get(reverse('main:cv_list'))
    assert response.status_code == 200


def test_cv_list_view_displays_cvs(client, cv1, cv2, skill_python):
    response = client.get(reverse('main:cv_list'))
    content = response.content.decode(response.charset)
    assert cv1.firstname in content
    assert cv1.lastname in content
    assert cv2.firstname in content
    assert cv2.lastname in content
    assert skill_python.name in content
    assert "Project Alpha" in content


def test_cv_list_view_empty_state(client):
    CV.objects.all().delete()
    response = client.get(reverse('main:cv_list'))
    assert response.status_code == 200
    assert "No CVs found." in response.content.decode(response.charset)


def test_cv_detail_view_status_code_for_existing_cv(client, cv1):
    response = client.get(reverse('main:cv_detail', args=[cv1.pk]))
    assert response.status_code == 200


def test_cv_detail_view_status_code_for_non_existent_cv(client):
    non_existent_pk = 10000000
    response = client.get(reverse('main:cv_detail', args=[non_existent_pk]))
    assert response.status_code == 404


def test_cv_detail_view_displays_cv_details(client, cv1, skill_django):
    response = client.get(reverse('main:cv_detail', args=[cv1.pk]))
    content = response.content.decode(response.charset)
    assert cv1.firstname in content
    assert cv1.lastname in content
    assert cv1.bio in content
    assert skill_django.name in content
    assert "Project Alpha" in content
    assert cv1.contacts['linkedin'] in content

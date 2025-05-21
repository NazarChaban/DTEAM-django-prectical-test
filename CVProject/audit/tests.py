from django.contrib.auth.models import AnonymousUser
from audit.models import RequestLog
from django.utils import timezone
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def create_logs():
    def _create(n=10):
        logs = []
        for i in range(n):
            log = RequestLog.objects.create(
                timestamp=timezone.now(),
                method='GET',
                path=f'/example-path-{i}/',
                query_string='param=value',
                ip_address='127.0.0.1',
                user=None
            )
            logs.append(log)
        return logs
    return _create


@pytest.fixture
def user_factory(django_user_model):
    def create_user(**kwargs):
        return django_user_model.objects.create_user(
            username=kwargs.get("username", "testuser"),
            password=kwargs.get("password", "password123"),
        )
    return create_user


class TestRequestLogModel:
    def test_str_representation(self):
        log = RequestLog.objects.create(
            timestamp=timezone.now(),
            method='POST',
            path='/some-path/',
        )
        assert str(log) == f"{log.timestamp} - POST /some-path/"

    def test_creation_with_user(self, user_factory):
        user = user_factory()
        log = RequestLog.objects.create(
            method='GET',
            path='/test-log/',
            query_string='a=1&b=2',
            ip_address='192.168.1.1',
            user=user
        )
        assert log.id is not None
        assert log.method == 'GET'
        assert log.path == '/test-log/'
        assert log.query_string == 'a=1&b=2'
        assert log.ip_address == '192.168.1.1'
        assert log.user == user


class TestRecentLogsView:
    def test_returns_10_latest_logs(self, client, create_logs):
        create_logs(n=15)
        url = reverse('audit:recent_logs')
        response = client.get(url)

        assert response.status_code == 200
        assert 'logs' in response.context

        logs = response.context['logs']
        assert len(logs) == 10

        timestamps = [log.timestamp for log in logs]
        assert timestamps == sorted(timestamps, reverse=True)


class TestRequestLogMiddleware:
    def test_creates_log_entry(self, client):
        assert RequestLog.objects.count() == 0

        url = reverse('audit:recent_logs')
        response = client.get(url)

        assert response.status_code == 200
        assert RequestLog.objects.count() == 1

        log = RequestLog.objects.first()
        assert log.method == 'GET'
        assert log.path == url
        assert log.user is None or isinstance(log.user, AnonymousUser)

    def test_logs_authenticated_user(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username='testuser', password='testpass'
        )
        client.login(username='testuser', password='testpass')

        url = reverse('audit:recent_logs')
        client.get(url)

        log = RequestLog.objects.last()
        assert log.user == user

    def test_saves_query_string(self, client):
        client.get('/logs/?q=test&limit=10')

        log = RequestLog.objects.last()
        assert 'q=test' in log.query_string
        assert 'limit=10' in log.query_string

from types import SimpleNamespace
from unittest import mock

import pytest

from app.api_client import ApiClient


def subject():
    return ApiClient(token="token", username="username", password="password")


def success_response():
    return SimpleNamespace(status_code=200)


def unauthorized_response():
    return SimpleNamespace(status_code=401)


def login_success_response():
    return SimpleNamespace(
        status_code=200,
        json=lambda: {"data": {"attributes": {"auth_token": "new_token"}}},
    )


def login_unauthorized_response():
    return SimpleNamespace(status_code=401, json=lambda: {"error": "Unauthorized"})


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_get_success(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.get.side_effect = [success_response()]
    requests_mock.post.side_effect = [login_success_response()]

    response = subject().get_request("test_endpoint")

    assert requests_mock.get.call_count == 1
    requests_mock.get.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                headers={"Authorization": "Bearer token"},
            )
        ]
    )
    assert requests_mock.post.call_count == 0
    assert response.status_code == 200


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_get_unauthorized_repeat_success(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.get.side_effect = [unauthorized_response(), success_response()]
    requests_mock.post.side_effect = [login_success_response()]

    response = subject().get_request("test_endpoint")

    assert requests_mock.get.call_count == 2
    requests_mock.get.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                headers={"Authorization": "Bearer token"},
            ),
            mock.call(
                "http://test_backend/test_endpoint",
                headers={"Authorization": "Bearer new_token"},
            ),
        ]
    )
    assert requests_mock.post.call_count == 1
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/api/v1/auth/login",
                data={"email": "username", "password": "password"},
            )
        ]
    )
    assert response.status_code == 200


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_get_unauthorized_repeat_unauthorized(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.get.side_effect = [unauthorized_response(), unauthorized_response()]
    requests_mock.post.side_effect = [login_success_response()]

    response = subject().get_request("test_endpoint")

    assert requests_mock.get.call_count == 2
    requests_mock.get.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                headers={"Authorization": "Bearer token"},
            ),
            mock.call(
                "http://test_backend/test_endpoint",
                headers={"Authorization": "Bearer new_token"},
            ),
        ]
    )
    assert requests_mock.post.call_count == 1
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/api/v1/auth/login",
                data={"email": "username", "password": "password"},
            )
        ]
    )
    assert response.status_code == 401


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_get_unauthorized_then_login_failure(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.get.side_effect = [unauthorized_response(), success_response()]
    requests_mock.post.side_effect = [login_unauthorized_response()]

    with pytest.raises(Exception) as excinfo:
        subject().get_request("test_endpoint")

    assert requests_mock.get.call_count == 1
    requests_mock.get.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                headers={"Authorization": "Bearer token"},
            )
        ]
    )
    assert requests_mock.post.call_count == 1
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/api/v1/auth/login",
                data={"email": "username", "password": "password"},
            )
        ]
    )
    assert "Unauthorized" in str(excinfo.value)


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_post_success(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.post.side_effect = [success_response()]

    response = subject().post_request("test_endpoint", {"data": "data"})

    assert requests_mock.post.call_count == 1
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                data={"data": "data"},
                headers={"Authorization": "Bearer token"},
            )
        ]
    )
    assert response.status_code == 200


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_post_unauthorized_repeat_success(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.post.side_effect = [
        unauthorized_response(),
        login_success_response(),
        success_response(),
    ]

    response = subject().post_request("test_endpoint", {"data": "data"})

    assert requests_mock.post.call_count == 3
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                data={"data": "data"},
                headers={"Authorization": "Bearer token"},
            ),
            mock.call(
                "http://test_backend/api/v1/auth/login",
                data={"email": "username", "password": "password"},
            ),
            mock.call(
                "http://test_backend/test_endpoint",
                data={"data": "data"},
                headers={"Authorization": "Bearer new_token"},
            ),
        ]
    )
    assert response.status_code == 200


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_post_unauthorized_repeat_unauthorized(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.post.side_effect = [
        unauthorized_response(),
        login_success_response(),
        unauthorized_response(),
    ]

    response = subject().post_request("test_endpoint", {"data": "data"})

    assert requests_mock.post.call_count == 3
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                data={"data": "data"},
                headers={"Authorization": "Bearer token"},
            ),
            mock.call(
                "http://test_backend/api/v1/auth/login",
                data={"email": "username", "password": "password"},
            ),
            mock.call(
                "http://test_backend/test_endpoint",
                data={"data": "data"},
                headers={"Authorization": "Bearer new_token"},
            ),
        ]
    )
    assert response.status_code == 401


@mock.patch("app.api_client.requests")
@mock.patch("app.api_client.os")
def test_post_unauthorized_then_login_failure(os_mock, requests_mock):
    os_mock.getenv.return_value = "http://test_backend"
    requests_mock.post.side_effect = [
        unauthorized_response(),
        login_unauthorized_response(),
    ]

    with pytest.raises(Exception) as excinfo:
        subject().post_request("test_endpoint", {"data": "data"})

    assert requests_mock.post.call_count == 2
    requests_mock.post.assert_has_calls(
        [
            mock.call(
                "http://test_backend/test_endpoint",
                data={"data": "data"},
                headers={"Authorization": "Bearer token"},
            ),
            mock.call(
                "http://test_backend/api/v1/auth/login",
                data={"email": "username", "password": "password"},
            ),
        ]
    )
    assert "Unauthorized" in str(excinfo.value)

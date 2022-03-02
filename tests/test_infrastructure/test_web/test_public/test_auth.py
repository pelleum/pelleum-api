from datetime import date, datetime
from typing import Mapping

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.usecases.schemas.users import UserResponse, UserWithAuthTokenResponse
from tests.conftest import NON_HASHED_USER_PASSWORD, TEST_USERNAME


@pytest_asyncio.fixture
async def create_user_request_json() -> Mapping[str, str]:
    return {
        "email": "test@test.com",
        "username": "test",
        "password": NON_HASHED_USER_PASSWORD,
        "gender": "MALE",
        "birthdate": "2002-11-27T06:00:00.000Z",
    }


@pytest_asyncio.fixture
async def updated_user_request_json() -> Mapping[str, str]:
    return {
        "email": "updatedtest@test.com",
        "username": "updatedtest",
    }


@pytest.mark.asyncio
async def test_login_for_access_token(
    test_client: AsyncClient,
) -> None:
    # Test successful login

    test_login_data = {
        "username": TEST_USERNAME,
        "password": NON_HASHED_USER_PASSWORD,
    }

    endpoint = "/public/auth/users/login"

    response = await test_client.post(endpoint, data=test_login_data)
    response_data = response.json()
    expected_response_fields = [field for field in UserWithAuthTokenResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key in test_login_data:
            assert value == test_login_data.get(key)

    # Test unsuccessful login
    test_wrong_login_data = {
        "username": TEST_USERNAME,
        "password": NON_HASHED_USER_PASSWORD + "wrong",
    }

    response = await test_client.post(endpoint, data=test_wrong_login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_new_user(
    test_client: AsyncClient, create_user_request_json: Mapping[str, str]
) -> None:

    endpoint = "/public/auth/users"

    # Test successful user creation
    response = await test_client.post(endpoint, json=create_user_request_json)
    response_data = response.json()
    expected_response_fields = [field for field in UserWithAuthTokenResponse.__fields__]

    # Assertions
    assert response.status_code == 201
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key in create_user_request_json:
            if key != "birthdate":
                assert value == create_user_request_json.get(key)
            else:
                assert isinstance(datetime.strptime(value, "%Y-%m-%d").date(), date)

    # Test invalid password
    json_copy = create_user_request_json.copy()
    json_copy["password"] = "wontwork"
    response = await test_client.post(endpoint, json=json_copy)
    assert response.status_code == 400

    # Test invalid username
    json_copy = create_user_request_json.copy()
    json_copy["username"] = "toolongtoolongtoolongtoolong"
    response = await test_client.post(endpoint, json=json_copy)
    assert response.status_code == 422

    # Test invalid username
    json_copy = create_user_request_json.copy()
    json_copy["email"] = "wontwork"
    response = await test_client.post(endpoint, json=json_copy)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_current_user(test_client: AsyncClient) -> None:

    endpoint = "/public/auth/users"

    response = await test_client.get(endpoint)
    response_data = response.json()
    expected_response_fields = [field for field in UserResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    for key in response_data:
        assert key in expected_response_fields


@pytest.mark.asyncio
async def test_update_user(
    test_client: AsyncClient, updated_user_request_json: Mapping[str, str]
) -> None:

    endpoint = "/public/auth/users"

    response = await test_client.patch(endpoint, json=updated_user_request_json)
    response_data = response.json()
    expected_response_fields = [field for field in UserWithAuthTokenResponse.__fields__]

    # Assertions
    assert response.status_code == 200
    for key, value in response_data.items():
        assert key in expected_response_fields
        if key in updated_user_request_json:
            assert value == updated_user_request_json.get(key)

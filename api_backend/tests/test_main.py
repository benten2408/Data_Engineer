import os

## Loading .env file ---------------------------------##
from dotenv import load_dotenv
dotenv_path = os.path.join(os.getcwd(), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
## -------------------------------------------------- ##

import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

from app.main import api  

import warnings
warnings.filterwarnings('ignore')

client = TestClient(api)

TEST_USERNAME = os.environ['TEST_USERNAME']
TEST_PASSWORD = os.environ['TEST_PASSWORD']
TEST_HASHED_PASSWORD = os.environ['TEST_HASHED_PASSWORD']

@pytest.mark.asyncio
async def test_get_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": 200, "message": "Bienvenue sur l'API Job Market"}

@pytest.mark.asyncio
@patch('app.auth_utils.users_db')
async def test_login_for_access_token(mock_user_db):
    test_user = {
        "username": TEST_USERNAME,
        "hashed_password": TEST_HASHED_PASSWORD,
    }
    mock_user_db.return_value = test_user

    async with AsyncClient(app=api, base_url="http://test") as ac:
        response = await ac.post(
            "/token", 
            data={
                "username": os.environ['TEST_USERNAME'], 
                "password": os.environ['TEST_PASSWORD']
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
@patch('app.main.get_current_user')
async def test_secure_endpoint_unauthorized(mock_get_current_user):
    mock_get_current_user.return_value = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    async with AsyncClient(app=api, base_url="http://test") as ac:
        response = await ac.get("/secure")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_secure_endpoint_authorized():
    async with AsyncClient(app=api, base_url="http://test") as ac:
        login_response = await ac.post(
            "/token", 
            data={
                "username": os.environ['TEST_USERNAME'], 
                "password": os.environ['TEST_PASSWORD']
            }
        )
        access_token = login_response.json().get("access_token")
        assert login_response.status_code == status.HTTP_200_OK
        assert access_token is not None

    async with AsyncClient(app=api, base_url="http://test") as ac:
        response = await ac.get("/secure", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": 'Access is True'}

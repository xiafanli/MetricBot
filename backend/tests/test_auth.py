import pytest
from fastapi import status


class TestHealthCheck:
    def test_health_check_returns_healthy(self, client):
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data


class TestAuthAPI:
    def test_register_user_success(self, client, test_user):
        response = client.post("/api/v1/auth/register", json=test_user)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]
        assert "id" in data
    
    def test_register_duplicate_user_fails(self, client, test_user):
        client.post("/api/v1/auth/register", json=test_user)
        
        response = client.post("/api/v1/auth/register", json=test_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, client, test_user):
        client.post("/api/v1/auth/register", json=test_user)
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password_fails(self, client, test_user):
        client.post("/api/v1/auth/register", json=test_user)
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_with_auth(self, client, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "username" in data
        assert "email" in data
    
    def test_get_current_user_without_auth_fails(self, client):
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

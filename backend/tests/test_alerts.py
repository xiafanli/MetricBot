import pytest
from fastapi import status


class TestAlertStatsAPI:
    def test_get_alert_stats_without_auth_fails(self, client):
        response = client.get("/api/v1/alerts/stats")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_alert_stats_with_auth(self, client, auth_headers):
        response = client.get("/api/v1/alerts/stats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "critical" in data
        assert "warning" in data
        assert "info" in data
        assert "resolved" in data
        assert "active" in data
        assert "today" in data
        assert "week" in data
        assert "resolution_rate" in data
    
    def test_alert_stats_initial_values(self, client, auth_headers):
        response = client.get("/api/v1/alerts/stats", headers=auth_headers)
        
        data = response.json()
        assert data["total"] == 0
        assert data["critical"] == 0
        assert data["warning"] == 0
        assert data["info"] == 0
        assert data["resolution_rate"] == 0.0


class TestAlertRulesAPI:
    def test_list_rules_empty(self, client, auth_headers):
        response = client.get("/api/v1/alerts/rules", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_alert_rule_success(self, client, auth_headers):
        rule_data = {
            "name": "CPU高使用率告警",
            "description": "CPU使用率超过80%时触发",
            "datasource_id": 1,
            "datasource_type": "prometheus",
            "metric_query": "cpu_usage",
            "condition_type": "greater_than",
            "threshold": 80.0,
            "severity": "warning",
            "evaluation_interval": 60,
            "enabled": True
        }
        
        response = client.post(
            "/api/v1/alerts/rules",
            json=rule_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == rule_data["name"]
        assert data["severity"] == rule_data["severity"]
        assert "id" in data

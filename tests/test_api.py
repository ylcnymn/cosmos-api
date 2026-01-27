"""
Unit and integration tests for CosmosAPI
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test all API endpoints"""
    
    def test_home_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
        assert "/bodies" in data["endpoints"]
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ephemeris_loaded"] == True
    
    def test_list_bodies(self):
        """Test bodies endpoint"""
        response = client.get("/bodies")
        assert response.status_code == 200
        data = response.json()
        assert "available_bodies" in data
        assert len(data["available_bodies"]) > 0
        assert "earth" in data["available_bodies"]
        assert "mars" in data["available_bodies"]
    
    def test_distance_calculation(self):
        """Test distance endpoint with valid bodies"""
        response = client.get("/distance?obj1=earth&obj2=mars")
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "earth"
        assert data["target"] == "mars"
        assert "km" in data
        assert "au" in data
        assert "light_time_seconds" in data
        assert data["km"] > 0
        assert data["au"] > 0
    
    def test_distance_invalid_body(self):
        """Test distance endpoint with invalid body"""
        response = client.get("/distance?obj1=earth&obj2=invalid_planet")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_position_calculation(self):
        """Test position endpoint with valid parameters"""
        response = client.get(
            "/position?planet=jupiter&lat=41.0082&lon=28.9784"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["planet"] == "jupiter"
        assert "altitude_deg" in data
        assert "azimuth_deg" in data
        assert "distance_km" in data
        assert "is_visible" in data
        assert -90 <= data["altitude_deg"] <= 90
        assert 0 <= data["azimuth_deg"] <= 360
    
    def test_position_invalid_coordinates(self):
        """Test position endpoint with invalid coordinates"""
        # Latitude out of range
        response = client.get("/position?planet=mars&lat=100&lon=0")
        assert response.status_code == 400
        
        # Longitude out of range
        response = client.get("/position?planet=mars&lat=0&lon=200")
        assert response.status_code == 400
    
    def test_position_invalid_planet(self):
        """Test position endpoint with invalid planet"""
        response = client.get("/position?planet=invalid&lat=0&lon=0")
        assert response.status_code == 400
    
    def test_distance_with_timestamp(self):
        """Test distance calculation with custom timestamp"""
        response = client.get(
            "/distance?obj1=earth&obj2=sun&at=2025-01-15T12:00:00Z"
        )
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "2025-01-15" in data["timestamp"]
    
    def test_position_with_timestamp(self):
        """Test position calculation with custom timestamp"""
        response = client.get(
            "/position?planet=mars&lat=41.0082&lon=28.9784&at=2025-01-15T20:00:00Z"
        )
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "2025-01-15" in data["timestamp"]
    
    def test_swagger_docs(self):
        """Test that Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema(self):
        """Test OpenAPI schema generation"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "/distance" in data["paths"]
        assert "/position" in data["paths"]

class TestValidation:
    """Test input validation"""
    
    def test_distance_missing_parameters(self):
        """Test that missing parameters are rejected"""
        # Missing obj1
        response = client.get("/distance?obj2=mars")
        assert response.status_code == 422
        
        # Missing obj2
        response = client.get("/distance?obj1=earth")
        assert response.status_code == 422
    
    def test_position_missing_parameters(self):
        """Test that missing position parameters are rejected"""
        # Missing planet
        response = client.get("/position?lat=0&lon=0")
        assert response.status_code == 422
        
        # Missing lat
        response = client.get("/position?planet=mars&lon=0")
        assert response.status_code == 422
        
        # Missing lon
        response = client.get("/position?planet=mars&lat=0")
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
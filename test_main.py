import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import os

# Set dummy environment variables for tests
os.environ.setdefault("GROQ_API_KEY", "test-key-12345")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key-67890")

from main import app, ai_service, db_service
from schemas import Lead

client = TestClient(app)


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test that root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "AI Business Automator API is running"}


class TestProcessLeadEndpoint:
    """Test /process-lead endpoint"""
    
    @patch.object(db_service, 'insert_lead')
    @patch.object(ai_service, 'process_lead_text')
    def test_process_lead_success(self, mock_ai_process, mock_db_insert):
        """Test successful lead processing"""
        # Mock responses
        mock_lead = Lead(
            name="Jan Kowalski",
            email="jan@example.com",
            phone="123-456-789",
            product="sales automation software",
            budget_est="10000 PLN",
            urgency="High",
            city="Warsaw",
            summary="Test lead",
            score=9
        )
        mock_ai_process.return_value = mock_lead
        mock_db_insert.return_value = {"success": True}
        
        # Make request
        response = client.post("/process-lead", json={
            "text": "Hi, I'm Jan Kowalski from Warsaw. Interested in sales automation."
        })
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jan Kowalski"
        assert data["email"] == "jan@example.com"
        assert data["city"] == "Warsaw"
        assert data["score"] == 9
    
    @patch.object(ai_service, 'process_lead_text')
    def test_process_lead_invalid_input(self, mock_ai_process):
        """Test with invalid input (empty text)"""
        mock_ai_process.side_effect = ValueError("Text cannot be empty")
        
        response = client.post("/process-lead", json={
            "text": ""
        })
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    @patch.object(db_service, 'insert_lead')
    @patch.object(ai_service, 'process_lead_text')
    def test_process_lead_database_error(self, mock_ai_process, mock_db_insert):
        """Test when database error occurs"""
        mock_lead = Lead(
            name="Test", email="test@test.com", phone="123",
            product="test", budget_est="1000", urgency="Low",
            city="Test", summary="test", score=5
        )
        mock_ai_process.return_value = mock_lead
        mock_db_insert.side_effect = Exception("Database connection failed")
        
        response = client.post("/process-lead", json={
            "text": "Test lead"
        })
        
        assert response.status_code == 500
    
    @patch.object(db_service, 'insert_lead')
    @patch.object(ai_service, 'process_lead_text')
    def test_process_lead_with_different_score(self, mock_ai_process, mock_db_insert):
        """Test lead with different score values"""
        for score in [1, 5, 10]:
            mock_lead = Lead(
                name="Test", email="test@test.com", phone="123",
                product="test", budget_est="1000", urgency="Low",
                city="Test", summary="test", score=score
            )
            mock_ai_process.return_value = mock_lead
            mock_db_insert.return_value = {"success": True}
            
            response = client.post("/process-lead", json={"text": f"Test with score {score}"})
            
            assert response.status_code == 200
            assert response.json()["score"] == score


class TestLeadSchema:
    """Test Lead data schema"""
    
    def test_lead_schema_validation(self):
        """Test that Lead schema validates required fields"""
        lead = Lead(
            name="John Doe",
            email="john@example.com",
            phone="123-456-789",
            product="Software",
            budget_est="5000",
            urgency="Medium",
            city="New York",
            summary="Good lead",
            score=7
        )
        
        assert lead.name == "John Doe"
        assert lead.score == 7
        assert lead.email == "john@example.com"
    
    def test_lead_schema_missing_field(self):
        """Test that Lead schema requires all fields"""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            Lead(
                name="John Doe",
                email="john@example.com",
                # Missing other required fields
            )


class TestEndpointInputValidation:
    """Test input validation for endpoints"""
    
    def test_process_lead_missing_text_field(self):
        """Test that endpoint rejects request missing 'text' field"""
        response = client.post("/process-lead", json={})
        assert response.status_code == 422  # Pydantic validation error
    
    def test_process_lead_invalid_json(self):
        """Test that endpoint handles invalid JSON"""
        response = client.post("/process-lead", data="invalid json")
        assert response.status_code == 422

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

# Set dummy environment variables for tests
os.environ.setdefault("GROQ_API_KEY", "test-key-12345")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key-67890")

from ai_service import AIService
from database import DatabaseService
from schemas import Lead


class TestAIService:
    """Test AI Service functionality"""
    
    @patch('ai_service.Groq')  # Mock Groq client class
    def test_ai_service_initialization(self, mock_groq_class):
        """Test AIService initializes correctly"""
        with patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'}):
            service = AIService()
            assert service is not None
            # Verify Groq was called with the API key
            mock_groq_class.assert_called_once_with(api_key='test-key')


class TestDatabaseService:
    """Test Database Service functionality"""
    
    @patch('database.create_client')
    def test_database_service_initialization(self, mock_create_client):
        """Test DatabaseService initializes correctly"""
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key'
        }):
            service = DatabaseService()
            assert service is not None
            mock_create_client.assert_called_once()
    
    @patch('database.create_client')
    def test_insert_lead_success(self, mock_create_client):
        """Test successful lead insertion"""
        mock_supabase = MagicMock()
        mock_create_client.return_value = mock_supabase
        
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key'
        }):
            service = DatabaseService()
            
            lead = Lead(
                name="John Doe",
                email="john@example.com",
                phone="123-456-789",
                product="Software",
                budget_est="5000",
                urgency="High",
                city="New York",
                summary="Good lead",
                score=8
            )
            
            mock_response = MagicMock()
            mock_response.data = [{"id": 1, **lead.model_dump()}]
            
            service.supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            result = service.insert_lead(lead)
            
            assert result["success"] is True
            assert len(result["data"]) > 0
    
    @patch('database.create_client')
    def test_insert_lead_database_error(self, mock_create_client):
        """Test database error handling"""
        mock_supabase = MagicMock()
        mock_create_client.return_value = mock_supabase
        
        with patch.dict('os.environ', {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key'
        }):
            service = DatabaseService()
            
            lead = Lead(
                name="John Doe",
                email="john@example.com",
                phone="123-456-789",
                product="Software",
                budget_est="5000",
                urgency="High",
                city="New York",
                summary="Good lead",
                score=8
            )
            
            # Simulate database error
            service.supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Connection failed")
            
            with pytest.raises(ValueError, match="Błąd podczas zapisywania do bazy"):
                service.insert_lead(lead)

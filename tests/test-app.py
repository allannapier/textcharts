"""
Tests for the Flask application
"""

import pytest
from flask import Flask
from app import create_app
from config import TestingConfig


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
    yield app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestApp:
    """Test cases for the Flask application"""
    
    def test_app_creation(self, app):
        """Test app is created correctly"""
        assert isinstance(app, Flask)
        assert app.config['TESTING'] is True
    
    def test_index_route(self, client):
        """Test index route"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Mermaid Diagram Builder' in response.data
    
    def test_404_error(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data
    
    def test_api_generate_diagram_no_data(self, client):
        """Test generate diagram API with no data"""
        response = client.post('/api/generate-diagram')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'No data provided' in data['error']
    
    def test_api_generate_diagram_empty_prompt(self, client):
        """Test generate diagram API with empty prompt"""
        response = client.post('/api/generate-diagram', 
                             json={'prompt': '', 'diagram_type': 'flowchart'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Prompt cannot be empty' in data['error']
    
    def test_api_generate_diagram_invalid_type(self, client):
        """Test generate diagram API with invalid diagram type"""
        response = client.post('/api/generate-diagram', 
                             json={'prompt': 'test diagram', 'diagram_type': 'invalid'})
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'Invalid diagram type' in data['error']
    
    def test_api_validate_syntax_no_data(self, client):
        """Test validate syntax API with no data"""
        response = client.post('/api/validate-syntax')
        assert response.status_code == 400
        data = response.get_json()
        assert data['is_valid'] is False
        assert 'No syntax provided' in data['error']
    
    def test_api_validate_syntax_valid(self, client):
        """Test validate syntax API with valid syntax"""
        response = client.post('/api/validate-syntax', 
                             json={'syntax': 'flowchart TD\n    A --> B', 
                                   'diagram_type': 'flowchart'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['is_valid'] is True
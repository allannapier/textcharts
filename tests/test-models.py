"""
Tests for data models
"""

import pytest
from datetime import datetime
from models import DiagramRequest, DiagramResponse, ValidationResult


class TestDiagramRequest:
    """Test cases for DiagramRequest model"""
    
    def test_valid_request(self):
        """Test valid diagram request"""
        request = DiagramRequest(
            prompt="Create a flowchart for login process",
            diagram_type="flowchart"
        )
        is_valid, error = request.validate()
        assert is_valid is True
        assert error is None
    
    def test_empty_prompt(self):
        """Test request with empty prompt"""
        request = DiagramRequest(prompt="", diagram_type="flowchart")
        is_valid, error = request.validate()
        assert is_valid is False
        assert "Prompt cannot be empty" in error
    
    def test_whitespace_prompt(self):
        """Test request with whitespace-only prompt"""
        request = DiagramRequest(prompt="   ", diagram_type="flowchart")
        is_valid, error = request.validate()
        assert is_valid is False
        assert "Prompt cannot be empty" in error
    
    def test_long_prompt(self):
        """Test request with prompt exceeding max length"""
        request = DiagramRequest(
            prompt="x" * 1001,
            diagram_type="flowchart"
        )
        is_valid, error = request.validate()
        assert is_valid is False
        assert "Prompt too long" in error
    
    def test_invalid_diagram_type(self):
        """Test request with invalid diagram type"""
        request = DiagramRequest(
            prompt="Create a diagram",
            diagram_type="invalid_type"
        )
        is_valid, error = request.validate()
        assert is_valid is False
        assert "Invalid diagram type" in error
    
    def test_all_valid_diagram_types(self):
        """Test all valid diagram types"""
        valid_types = ['flowchart', 'sequence', 'classDiagram', 'stateDiagram', 
                      'erDiagram', 'journey', 'gantt', 'pie', 'quadrantChart', 'mindmap']
        
        for diagram_type in valid_types:
            request = DiagramRequest(
                prompt="Test prompt",
                diagram_type=diagram_type
            )
            is_valid, error = request.validate()
            assert is_valid is True
            assert error is None


class TestDiagramResponse:
    """Test cases for DiagramResponse model"""
    
    def test_successful_response(self):
        """Test successful diagram response"""
        response = DiagramResponse(
            syntax="flowchart TD\n    A --> B",
            diagram_type="flowchart",
            success=True
        )
        assert response.syntax == "flowchart TD\n    A --> B"
        assert response.diagram_type == "flowchart"
        assert response.success is True
        assert response.error is None
        assert isinstance(response.timestamp, datetime)
    
    def test_error_response(self):
        """Test error diagram response"""
        response = DiagramResponse(
            syntax="",
            diagram_type="flowchart",
            success=False,
            error="API error occurred"
        )
        assert response.syntax == ""
        assert response.diagram_type == "flowchart"
        assert response.success is False
        assert response.error == "API error occurred"
        assert isinstance(response.timestamp, datetime)
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        response = DiagramResponse(
            syntax="flowchart TD\n    A --> B",
            diagram_type="flowchart",
            success=True
        )
        data = response.to_dict()
        
        assert isinstance(data, dict)
        assert data['syntax'] == "flowchart TD\n    A --> B"
        assert data['diagram_type'] == "flowchart"
        assert data['success'] is True
        assert data['error'] is None
        assert isinstance(data['timestamp'], str)
    
    def test_custom_timestamp(self):
        """Test response with custom timestamp"""
        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        response = DiagramResponse(
            syntax="test",
            diagram_type="flowchart",
            success=True,
            timestamp=custom_time
        )
        assert response.timestamp == custom_time


class TestValidationResult:
    """Test cases for ValidationResult model"""
    
    def test_valid_result(self):
        """Test valid validation result"""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.error is None
        assert result.line_number is None
    
    def test_invalid_result(self):
        """Test invalid validation result"""
        result = ValidationResult(
            is_valid=False,
            error="Syntax error",
            line_number=5
        )
        assert result.is_valid is False
        assert result.error == "Syntax error"
        assert result.line_number == 5
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        result = ValidationResult(
            is_valid=False,
            error="Invalid syntax",
            line_number=3
        )
        data = result.to_dict()
        
        assert isinstance(data, dict)
        assert data['is_valid'] is False
        assert data['error'] == "Invalid syntax"
        assert data['line_number'] == 3
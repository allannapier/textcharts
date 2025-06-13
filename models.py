"""
Data models for the Mermaid Diagram Builder
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class DiagramRequest:
    """Model for diagram generation request"""
    prompt: str
    diagram_type: str
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate the diagram request
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.prompt or not self.prompt.strip():
            return False, "Prompt cannot be empty"
        
        if len(self.prompt) > 1000:
            return False, "Prompt too long (max 1000 characters)"
        
        valid_types = ['flowchart', 'sequence', 'classDiagram', 'stateDiagram', 
                      'erDiagram', 'journey', 'gantt', 'pie', 'quadrantChart', 'mindmap']
        
        if self.diagram_type not in valid_types:
            return False, f"Invalid diagram type. Must be one of: {', '.join(valid_types)}"
        
        return True, None


@dataclass
class DiagramResponse:
    """Model for diagram generation response"""
    syntax: str
    diagram_type: str
    success: bool
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'syntax': self.syntax,
            'diagram_type': self.diagram_type,
            'success': self.success,
            'error': self.error,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class ValidationResult:
    """Model for syntax validation result"""
    is_valid: bool
    error: Optional[str] = None
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'is_valid': self.is_valid,
            'error': self.error,
            'line_number': self.line_number
        }
"""
Diagram service for validating Mermaid syntax
"""

import re
from typing import Optional, List, Tuple

from models import ValidationResult


class DiagramService:
    """Service for diagram-related operations"""
    
    def validate_syntax(self, syntax: str, diagram_type: str) -> ValidationResult:
        """
        Validate Mermaid syntax
        
        Args:
            syntax: Mermaid syntax to validate
            diagram_type: Type of diagram
            
        Returns:
            ValidationResult indicating if syntax is valid
        """
        if not syntax or not syntax.strip():
            return ValidationResult(is_valid=False, error="Syntax cannot be empty")
        
        # Check if syntax starts with valid diagram declaration
        valid_start = self._check_diagram_start(syntax, diagram_type)
        if not valid_start[0]:
            return ValidationResult(
                is_valid=False, 
                error=valid_start[1],
                line_number=1
            )
        
        # Perform type-specific validation
        validation_method = getattr(self, f'_validate_{diagram_type}', None)
        if validation_method:
            return validation_method(syntax)
        
        # Default validation - just check basic structure
        return self._basic_validation(syntax)
    
    def _check_diagram_start(self, syntax: str, diagram_type: str) -> Tuple[bool, Optional[str]]:
        """
        Check if syntax starts with correct diagram declaration
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        first_line = syntax.strip().split('\n')[0].strip()
        
        valid_starts = {
            'flowchart': ['flowchart', 'graph'],
            'sequence': ['sequenceDiagram'],
            'classDiagram': ['classDiagram'],
            'stateDiagram': ['stateDiagram', 'stateDiagram-v2'],
            'erDiagram': ['erDiagram'],
            'journey': ['journey'],
            'gantt': ['gantt'],
            'pie': ['pie'],
            'quadrantChart': ['quadrantChart'],
            'mindmap': ['mindmap']
        }
        
        expected_starts = valid_starts.get(diagram_type, [])
        
        for start in expected_starts:
            if first_line.startswith(start):
                return True, None
        
        return False, f"Diagram must start with one of: {', '.join(expected_starts)}"
    
    def _basic_validation(self, syntax: str) -> ValidationResult:
        """
        Basic syntax validation common to all diagram types
        """
        lines = syntax.strip().split('\n')
        
        # Check for balanced brackets/parentheses
        bracket_count = 0
        paren_count = 0
        
        for i, line in enumerate(lines, 1):
            bracket_count += line.count('[') - line.count(']')
            paren_count += line.count('(') - line.count(')')
            
            if bracket_count < 0:
                return ValidationResult(
                    is_valid=False,
                    error="Unmatched closing bracket ']'",
                    line_number=i
                )
            if paren_count < 0:
                return ValidationResult(
                    is_valid=False,
                    error="Unmatched closing parenthesis ')'",
                    line_number=i
                )
        
        if bracket_count != 0:
            return ValidationResult(
                is_valid=False,
                error="Unmatched opening bracket '['"
            )
        if paren_count != 0:
            return ValidationResult(
                is_valid=False,
                error="Unmatched opening parenthesis '('"
            )
        
        return ValidationResult(is_valid=True)
    
    def _validate_flowchart(self, syntax: str) -> ValidationResult:
        """Validate flowchart syntax"""
        lines = syntax.strip().split('\n')
        
        # Check for valid flowchart direction
        first_line = lines[0].strip()
        valid_directions = ['TD', 'TB', 'BT', 'LR', 'RL']
        
        if first_line.startswith('flowchart'):
            parts = first_line.split()
            if len(parts) > 1 and parts[1] not in valid_directions:
                return ValidationResult(
                    is_valid=False,
                    error=f"Invalid flowchart direction. Must be one of: {', '.join(valid_directions)}",
                    line_number=1
                )
        
        return self._basic_validation(syntax)
    
    def _validate_sequence(self, syntax: str) -> ValidationResult:
        """Validate sequence diagram syntax"""
        lines = syntax.strip().split('\n')
        
        for i, line in enumerate(lines[1:], 2):  # Skip first line
            line = line.strip()
            if not line:
                continue
            
            # Check for valid sequence diagram elements
            valid_patterns = [
                r'participant\s+\w+',
                r'actor\s+\w+',
                r'\w+\s*->>[-+]?\s*\w+\s*:',
                r'\w+\s*-->>[-+]?\s*\w+\s*:',
                r'Note\s+(right|left|over)\s+of\s+\w+',
                r'loop\s+',
                r'alt\s+',
                r'else\s*',
                r'end\s*'
            ]
            
            if not any(re.match(pattern, line) for pattern in valid_patterns):
                # Check if it might be a continuation of previous line
                if ':' not in line and not line.startswith(('Note', 'loop', 'alt', 'else', 'end')):
                    continue
                    
        return self._basic_validation(syntax)
    
    def _validate_classDiagram(self, syntax: str) -> ValidationResult:
        """Validate class diagram syntax"""
        return self._basic_validation(syntax)
    
    def _validate_stateDiagram(self, syntax: str) -> ValidationResult:
        """Validate state diagram syntax"""
        return self._basic_validation(syntax)
    
    def _validate_erDiagram(self, syntax: str) -> ValidationResult:
        """Validate ER diagram syntax"""
        lines = syntax.strip().split('\n')
        
        for i, line in enumerate(lines[1:], 2):  # Skip first line
            line = line.strip()
            if not line:
                continue
            
            # Check for valid ER diagram relationships
            if not re.match(r'\w+\s+\|[\|o\{]--[\|o\}]\|\s+\w+\s*:', line):
                # Could be an attribute definition
                if not re.match(r'\s+\w+\s+\w+', line):
                    pass  # Allow other valid syntax
        
        return self._basic_validation(syntax)
    
    def _validate_journey(self, syntax: str) -> ValidationResult:
        """Validate user journey syntax"""
        return self._basic_validation(syntax)
    
    def _validate_gantt(self, syntax: str) -> ValidationResult:
        """Validate Gantt chart syntax"""
        return self._basic_validation(syntax)
    
    def _validate_pie(self, syntax: str) -> ValidationResult:
        """Validate pie chart syntax"""
        lines = syntax.strip().split('\n')
        
        for i, line in enumerate(lines[1:], 2):  # Skip first line
            line = line.strip()
            if not line:
                continue
            
            # Check for valid pie chart entries (label : value)
            if not line.startswith('title') and ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    try:
                        # Try to parse the value as a number
                        float(parts[1].strip().strip('"'))
                    except ValueError:
                        return ValidationResult(
                            is_valid=False,
                            error="Pie chart values must be numbers",
                            line_number=i
                        )
        
        return self._basic_validation(syntax)
    
    def _validate_quadrantChart(self, syntax: str) -> ValidationResult:
        """Validate quadrant chart syntax"""
        return self._basic_validation(syntax)
    
    def _validate_mindmap(self, syntax: str) -> ValidationResult:
        """Validate mindmap syntax"""
        return self._
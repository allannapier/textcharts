"""
Tests for services
"""

import pytest
from services.diagram_service import DiagramService
from models import ValidationResult


class TestDiagramService:
    """Test cases for DiagramService"""
    
    @pytest.fixture
    def service(self):
        """Create diagram service instance"""
        return DiagramService()
    
    def test_validate_empty_syntax(self, service):
        """Test validation of empty syntax"""
        result = service.validate_syntax("", "flowchart")
        assert result.is_valid is False
        assert "Syntax cannot be empty" in result.error
    
    def test_validate_whitespace_syntax(self, service):
        """Test validation of whitespace-only syntax"""
        result = service.validate_syntax("   \n  ", "flowchart")
        assert result.is_valid is False
        assert "Syntax cannot be empty" in result.error
    
    def test_validate_valid_flowchart(self, service):
        """Test validation of valid flowchart"""
        syntax = """flowchart TD
            A[Start] --> B{Decision}
            B -->|Yes| C[Action 1]
            B -->|No| D[Action 2]
            C --> E[End]
            D --> E"""
        result = service.validate_syntax(syntax, "flowchart")
        assert result.is_valid is True
        assert result.error is None
    
    def test_validate_invalid_flowchart_direction(self, service):
        """Test validation of flowchart with invalid direction"""
        syntax = "flowchart XY\n    A --> B"
        result = service.validate_syntax(syntax, "flowchart")
        assert result.is_valid is False
        assert "Invalid flowchart direction" in result.error
        assert result.line_number == 1
    
    def test_validate_valid_sequence_diagram(self, service):
        """Test validation of valid sequence diagram"""
        syntax = """sequenceDiagram
            participant A as Alice
            participant B as Bob
            A->>B: Hello Bob
            B->>A: Hi Alice"""
        result = service.validate_syntax(syntax, "sequence")
        assert result.is_valid is True
    
    def test_validate_valid_class_diagram(self, service):
        """Test validation of valid class diagram"""
        syntax = """classDiagram
            class Animal {
                +String name
                +int age
                +makeSound()
            }
            class Dog {
                +bark()
            }
            Animal <|-- Dog"""
        result = service.validate_syntax(syntax, "classDiagram")
        assert result.is_valid is True
    
    def test_validate_valid_state_diagram(self, service):
        """Test validation of valid state diagram"""
        syntax = """stateDiagram-v2
            [*] --> Still
            Still --> [*]
            Still --> Moving
            Moving --> Still
            Moving --> Crash
            Crash --> [*]"""
        result = service.validate_syntax(syntax, "stateDiagram")
        assert result.is_valid is True
    
    def test_validate_valid_er_diagram(self, service):
        """Test validation of valid ER diagram"""
        syntax = """erDiagram
            CUSTOMER ||--o{ ORDER : places
            ORDER ||--|{ LINE-ITEM : contains
            CUSTOMER {
                string name
                string email
            }"""
        result = service.validate_syntax(syntax, "erDiagram")
        assert result.is_valid is True
    
    def test_validate_valid_journey(self, service):
        """Test validation of valid user journey"""
        syntax = """journey
            title My working day
            section Go to work
                Make tea: 5: Me
                Go upstairs: 3: Me
                Do work: 1: Me, Cat
            section Go home
                Go downstairs: 5: Me
                Sit down: 5: Me"""
        result = service.validate_syntax(syntax, "journey")
        assert result.is_valid is True
    
    def test_validate_valid_gantt(self, service):
        """Test validation of valid Gantt chart"""
        syntax = """gantt
            title A Gantt Diagram
            dateFormat YYYY-MM-DD
            section Section
                A task :a1, 2024-01-01, 30d
                Another task :after a1, 20d"""
        result = service.validate_syntax(syntax, "gantt")
        assert result.is_valid is True
    
    def test_validate_valid_pie(self, service):
        """Test validation of valid pie chart"""
        syntax = """pie title Pets adopted
            "Dogs" : 386
            "Cats" : 85
            "Rats" : 15"""
        result = service.validate_syntax(syntax, "pie")
        assert result.is_valid is True
    
    def test_validate_invalid_pie_values(self, service):
        """Test validation of pie chart with invalid values"""
        syntax = """pie title Invalid Chart
            "Dogs" : abc
            "Cats" : 85"""
        result = service.validate_syntax(syntax, "pie")
        assert result.is_valid is False
        assert "must be numbers" in result.error
    
    def test_validate_valid_quadrant_chart(self, service):
        """Test validation of valid quadrant chart"""
        syntax = """quadrantChart
            title Reach and engagement
            x-axis Low Reach --> High Reach
            y-axis Low Engagement --> High Engagement
            quadrant-1 We should expand
            quadrant-2 Need to promote
            quadrant-3 Re-evaluate
            quadrant-4 May be improved"""
        result = service.validate_syntax(syntax, "quadrantChart")
        assert result.is_valid is True
    
    def test_validate_valid_mindmap(self, service):
        """Test validation of valid mindmap"""
        syntax = """mindmap
          root((mindmap))
            Origins
              Long history
              Popularisation
            Research
              On effectiveness
              On features"""
        result = service.validate_syntax(syntax, "mindmap")
        assert result.is_valid is True
    
    def test_validate_unmatched_brackets(self, service):
        """Test validation with unmatched brackets"""
        syntax = """flowchart TD
            A[Start --> B
            B --> C]End"""
        result = service.validate_syntax(syntax, "flowchart")
        assert result.is_valid is False
        assert "Unmatched" in result.error
    
    def test_validate_unmatched_parentheses(self, service):
        """Test validation with unmatched parentheses"""
        syntax = """flowchart TD
            A((Start) --> B
            B --> C"""
        result = service.validate_syntax(syntax, "flowchart")
        assert result.is_valid is False
        assert "Unmatched" in result.error
    
    def test_wrong_diagram_type_declaration(self, service):
        """Test validation when syntax doesn't match diagram type"""
        syntax = "sequenceDiagram\n    participant A"
        result = service.validate_syntax(syntax, "flowchart")
        assert result.is_valid is False
        assert "must start with" in result.error
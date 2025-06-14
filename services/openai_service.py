"""
OpenAI service for generating Mermaid diagram syntax
"""

from openai import OpenAI
from flask import current_app
import logging
from typing import Optional

from models import DiagramResponse

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self):
        """Initialize the OpenAI service"""
        self.client = None
    
    def _get_client(self):
        """Get the OpenAI client"""
        if not self.client:
            api_key = current_app.config.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = OpenAI(api_key=api_key)
        return self.client
    
    def generate_diagram_syntax(self, prompt: str, diagram_type: str, previous_syntax: Optional[str] = None) -> DiagramResponse:
        """
        Generate Mermaid diagram syntax from natural language prompt
        
        Args:
            prompt: Natural language description of the diagram
            diagram_type: Type of diagram to generate
            previous_syntax: Previous diagram syntax for iterative updates
            
        Returns:
            DiagramResponse with generated syntax or error
        """
        try:
            client = self._get_client()
            
            # Construct the system prompt
            system_prompt = self._get_system_prompt(diagram_type)
            
            # Prepare user message with context if iterating
            user_message = prompt
            if previous_syntax:
                user_message = f"Here is the current diagram:\n\n{previous_syntax}\n\nNow modify it based on this request: {prompt}"
            
            # Make API call using official OpenAI client
            response = client.chat.completions.create(
                model=current_app.config['OPENAI_MODEL'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=current_app.config['OPENAI_TEMPERATURE'],
                max_tokens=current_app.config['OPENAI_MAX_TOKENS']
            )
            
            # Extract syntax from response
            syntax = response.choices[0].message.content.strip()
            
            # Clean up syntax (remove markdown code blocks if present)
            syntax = self._clean_syntax(syntax)
            
            return DiagramResponse(
                syntax=syntax,
                diagram_type=diagram_type,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating diagram syntax: {str(e)}")
            return DiagramResponse(
                syntax='',
                diagram_type=diagram_type,
                success=False,
                error=f"API request failed: {str(e)}"
            )
    
    def _get_system_prompt(self, diagram_type: str) -> str:
        """
        Get the system prompt for the specific diagram type
        
        Args:
            diagram_type: Type of diagram
            
        Returns:
            System prompt string
        """
        base_prompt = """You are a Mermaid diagram syntax generator. 
You MUST respond with ONLY valid Mermaid syntax - no explanations, no markdown code blocks, no additional text.
Generate clean, well-structured Mermaid syntax based EXACTLY on the user's description.
IMPORTANT: Only include the steps, elements, or components that the user explicitly mentions. Do NOT add any additional steps, elements, or details that are not specifically requested by the user."""

        type_specific_prompts = {
            'flowchart': """
Generate a flowchart using Mermaid syntax.
Use 'flowchart TD' or 'flowchart LR' for top-down or left-right layouts.
Example format:
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]""",
            
            'sequence': """
Generate a sequence diagram using Mermaid syntax.
Example format:
sequenceDiagram
    participant A as Alice
    participant B as Bob
    A->>B: Hello Bob
    B->>A: Hi Alice""",
            
            'classDiagram': """
Generate a class diagram using Mermaid syntax.
Example format:
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }""",
            
            'stateDiagram': """
Generate a state diagram using Mermaid syntax.
Example format:
stateDiagram-v2
    [*] --> State1
    State1 --> State2
    State2 --> [*]""",
            
            'erDiagram': """
Generate an entity relationship diagram using Mermaid syntax.
Example format:
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains""",
            
            'journey': """
Generate a user journey diagram using Mermaid syntax.
Example format:
journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me""",
            
            'gantt': """
Generate a Gantt chart using Mermaid syntax.
Example format:
gantt
    title A Gantt Diagram
    dateFormat YYYY-MM-DD
    section Section
        A task :a1, 2024-01-01, 30d""",
            
            'pie': """
Generate a pie chart using Mermaid syntax.
Example format:
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15""",
            
            'quadrantChart': """
Generate a quadrant chart using Mermaid syntax.
Example format:
quadrantChart
    title Reach and engagement
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved""",
            
            'mindmap': """
Generate a mindmap using Mermaid syntax.
Example format:
mindmap
  root((mindmap))
    Origins
      Long history
      Popularisation
    Research
      On effectiveness
      On features"""
        }
        
        specific_prompt = type_specific_prompts.get(diagram_type, '')
        return f"{base_prompt}\n\n{specific_prompt}"
    
    def _clean_syntax(self, syntax: str) -> str:
        """
        Clean up the generated syntax
        
        Args:
            syntax: Raw syntax from OpenAI
            
        Returns:
            Cleaned syntax
        """
        # Remove markdown code blocks
        if syntax.startswith('```'):
            lines = syntax.split('\n')
            if len(lines) > 2:
                # Remove first and last lines (code block markers)
                syntax = '\n'.join(lines[1:-1])
        
        # Remove 'mermaid' keyword if it's on the first line
        lines = syntax.strip().split('\n')
        if lines and lines[0].strip().lower() == 'mermaid':
            syntax = '\n'.join(lines[1:])
        
        return syntax.strip()
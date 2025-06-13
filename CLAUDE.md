# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Install dependencies
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Required environment variables in .env file:
OPENAI_API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here
```

### Running the Application
```bash
# Using virtual environment python directly
./venv/bin/python app.py

# Or activate venv first
source venv/bin/activate
python app.py
```
The application runs on http://localhost:5000 by default.

### Testing
```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test-app.py
```

## Architecture Overview

This is a Flask web application that generates Mermaid diagrams from natural language descriptions using OpenAI's GPT-4o-mini model.

### Core Architecture
- **Application Factory Pattern**: `app.py` uses `create_app()` factory for better testability
- **Blueprint Structure**: Routes are organized into `main_bp` (web pages) and `api_bp` (API endpoints)
- **Service Layer**: Business logic is separated into `services/` directory
- **Type Safety**: Full type hints throughout the codebase using Python 3.10+ syntax

### Key Components
1. **OpenAI Integration**: `services/openai_service.py` handles API calls with diagram-specific system prompts
2. **Validation**: `services/diagram_service.py` validates Mermaid syntax
3. **Data Models**: `models.py` contains dataclasses with validation methods
4. **Configuration**: `config.py` manages environment-based configs with different classes for dev/test/prod

### Request Flow
1. User submits natural language prompt via web interface
2. `routes.py` validates request using `DiagramRequest` model
3. `OpenAIService` generates Mermaid syntax with diagram-specific prompts
4. Frontend renders diagram using Mermaid.js library
5. Optional: `DiagramService` validates generated syntax

### Supported Diagram Types
Configured in `config.py` DIAGRAM_TYPES: flowchart, sequence, classDiagram, stateDiagram, erDiagram, journey, gantt, pie, quadrantChart, mindmap.

## Development Notes

### Adding New Diagram Types
1. Add to `DIAGRAM_TYPES` in `config.py`
2. Add system prompt in `OpenAIService._get_system_prompt()`
3. Add validation logic in `DiagramService` if needed
4. Add test cases in `test_services.py`

### Error Handling
- API routes return JSON with `success` boolean and `error` message
- Web routes render custom error templates (`templates/error/`)
- All services use proper exception handling with logging

### Configuration Management
- Uses environment variables with fallback defaults
- Separate config classes for different environments
- OpenAI settings (model, temperature, max_tokens) configurable via config
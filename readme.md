# Mermaid Diagram Builder

A Flask web application that generates Mermaid diagrams from natural language descriptions using OpenAI's GPT-4o-mini model.

## Features

- **Natural Language to Diagram**: Describe your diagram in plain English and get Mermaid syntax
- **Live Preview**: See your diagram update in real-time as you edit the syntax
- **Multiple Diagram Types**: Support for flowcharts, sequence diagrams, class diagrams, state diagrams, ER diagrams, user journeys, Gantt charts, pie charts, quadrant charts, and mind maps
- **Manual Editing**: Edit the generated syntax with live preview updates
- **Export to PNG**: Download your diagrams as PNG images
- **Responsive Design**: Works on desktop and mobile devices

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── models.py              # Data models with validation
├── routes.py              # HTTP route handlers
├── services/              # Business logic layer
│   ├── openai_service.py  # OpenAI API integration
│   └── diagram_service.py # Diagram validation logic
├── templates/             # Jinja2 HTML templates
├── static/                # CSS, JavaScript, and images
└── tests/                 # Comprehensive test suite
```

### Key Components

1. **Flask Application**: Uses application factory pattern for better testability
2. **Type Hints**: Full static typing throughout the codebase
3. **Service Layer**: Separates business logic from route handlers
4. **Data Models**: Pydantic-style dataclasses with validation
5. **Error Handling**: Comprehensive error handling with custom error pages
6. **Testing**: Unit tests with pytest achieving good coverage

## How It Works

1. **User Input**: User enters a natural language description of their desired diagram
2. **OpenAI Processing**: The description is sent to OpenAI's GPT-4o-mini model with a carefully crafted prompt
3. **Syntax Generation**: OpenAI returns pure Mermaid syntax (no explanations or markdown)
4. **Live Rendering**: Mermaid.js renders the syntax into a visual diagram
5. **Real-time Editing**: Users can manually edit the syntax with debounced live updates
6. **Export**: Diagrams can be exported as PNG images using canvas rendering

## Installation

1. Clone the repository:
```bash
cd C:\Users\anapi\code
git clone <repository-url> mermaid-diagram-builder
cd mermaid-diagram-builder
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
# Create a .env file in the project root
echo OPENAI_API_KEY=your-api-key-here > .env
echo SECRET_KEY=your-secret-key-here >> .env
```

## Configuration

The application uses environment variables for configuration:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: Flask secret key for sessions (optional, defaults to dev key)

Additional configuration options in `config.py`:
- `OPENAI_MODEL`: GPT model to use (default: gpt-4o-mini)
- `OPENAI_TEMPERATURE`: Temperature for generation (default: 0.2)
- `OPENAI_MAX_TOKENS`: Maximum tokens for response (default: 1000)

## Usage

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the application:
   - Enter a description of your diagram in the left panel
   - Select the diagram type from the dropdown
   - Click "Generate" to create the diagram
   - Edit the syntax manually if needed
   - Export the diagram as PNG when satisfied

### Example Prompts

**Flowchart**: "Create a login flow with email validation, password check, and two-factor authentication"

**Sequence Diagram**: "Show the interaction between a user, web server, and database for a product purchase"

**Class Diagram**: "Design a system for a library with books, members, and lending operations"

## API Endpoints

### `POST /api/generate-diagram`
Generate Mermaid syntax from natural language.

**Request Body**:
```json
{
  "prompt": "Description of the diagram",
  "diagram_type": "flowchart"
}
```

**Response**:
```json
{
  "syntax": "flowchart TD\n    A[Start] --> B[End]",
  "diagram_type": "flowchart",
  "success": true,
  "error": null,
  "timestamp": "2024-01-01T12:00:00"
}
```

### `POST /api/validate-syntax`
Validate Mermaid syntax.

**Request Body**:
```json
{
  "syntax": "flowchart TD\n    A --> B",
  "diagram_type": "flowchart"
}
```

**Response**:
```json
{
  "is_valid": true,
  "error": null,
  "line_number": null
}
```

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and returns
- Document all functions with docstrings
- Keep functions focused and single-purpose

### Adding New Diagram Types
1. Add the type to `DIAGRAM_TYPES` in `config.py`
2. Add a system prompt in `openai_service.py`
3. Add validation logic in `diagram_service.py`
4. Add test cases in `test_services.py`

### DRY Principles
- Shared functionality is extracted to service classes
- Configuration is centralized in `config.py`
- Common HTML structure uses Jinja2 template inheritance
- Validation logic is reusable across diagram types

## Security Considerations

- API keys are stored in environment variables, never in code
- Input validation prevents prompt injection
- Syntax validation prevents malicious diagram code
- Rate limiting should be added for production use
- CORS headers should be configured for production

## Future Enhancements

- Add user authentication and diagram saving
- Implement diagram sharing functionality
- Add more diagram types (Git graphs, Timeline diagrams)
- Support for custom themes and styling
- Collaborative editing features
- API rate limiting and caching
- Webhook support for CI/CD integration

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Acknowledgments

- [Mermaid.js](https://mermaid-js.github.io/) for diagram rendering
- [OpenAI](https://openai.com/) for natural language processing
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for UI components
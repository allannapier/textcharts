"""
Route definitions for the Mermaid Diagram Builder
"""

from flask import Blueprint, render_template, jsonify, request, current_app, session
from typing import Tuple, Dict, Any
import logging

from models import DiagramRequest, DiagramResponse, ValidationResult, DiagramSession
from services.openai_service import OpenAIService
from services.diagram_service import DiagramService

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize services
openai_service = OpenAIService()
diagram_service = DiagramService()

# Logger
logger = logging.getLogger(__name__)


@main_bp.route('/')
def index():
    """Render the main diagram builder interface"""
    diagram_types = current_app.config['DIAGRAM_TYPES']
    return render_template('index.html', diagram_types=diagram_types)


@api_bp.route('/generate-diagram', methods=['POST'])
def generate_diagram() -> Tuple[Dict[str, Any], int]:
    """
    Generate diagram syntax from natural language prompt
    
    Returns:
        JSON response with generated syntax or error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Create and validate request
        diagram_request = DiagramRequest(
            prompt=data.get('prompt', ''),
            diagram_type=data.get('diagram_type', 'flowchart'),
            is_iteration=data.get('is_iteration', False)
        )
        
        is_valid, error_msg = diagram_request.validate()
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Get or create session state
        session_data = session.get('diagram_session', {})
        diagram_session = DiagramSession.from_dict(session_data)
        
        # For new diagram types or non-iterations, clear session
        if diagram_request.diagram_type != diagram_session.diagram_type and not diagram_request.is_iteration:
            diagram_session = DiagramSession(diagram_type=diagram_request.diagram_type)
        
        # Generate diagram syntax with context if iterating
        previous_syntax = diagram_session.current_syntax if diagram_request.is_iteration else None
        response = openai_service.generate_diagram_syntax(
            prompt=diagram_request.prompt,
            diagram_type=diagram_request.diagram_type,
            previous_syntax=previous_syntax
        )
        
        # Update session if successful
        if response.success:
            diagram_session.add_to_history(response.syntax)
            diagram_session.diagram_type = diagram_request.diagram_type
            session['diagram_session'] = diagram_session.to_dict()
        
        return jsonify(response.to_dict()), 200 if response.success else 500
        
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'An unexpected error occurred'
        }), 500


@api_bp.route('/validate-syntax', methods=['POST'])
def validate_syntax() -> Tuple[Dict[str, Any], int]:
    """
    Validate Mermaid syntax
    
    Returns:
        JSON response with validation result
    """
    try:
        data = request.get_json()
        
        if not data or 'syntax' not in data:
            return jsonify({
                'is_valid': False, 
                'error': 'No syntax provided'
            }), 400
        
        syntax = data.get('syntax', '')
        diagram_type = data.get('diagram_type', 'flowchart')
        
        # Validate syntax
        result = diagram_service.validate_syntax(syntax, diagram_type)
        
        return jsonify(result.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error validating syntax: {str(e)}")
        return jsonify({
            'is_valid': False,
            'error': 'An unexpected error occurred'
        }), 500


@api_bp.route('/clear-session', methods=['POST'])
def clear_session() -> Tuple[Dict[str, Any], int]:
    """
    Clear the diagram session
    
    Returns:
        JSON response confirming session cleared
    """
    try:
        session.pop('diagram_session', None)
        return jsonify({'success': True, 'message': 'Session cleared'}), 200
        
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@api_bp.route('/session-info', methods=['GET'])
def get_session_info() -> Tuple[Dict[str, Any], int]:
    """
    Get current session information
    
    Returns:
        JSON response with session data
    """
    try:
        session_data = session.get('diagram_session', {})
        diagram_session = DiagramSession.from_dict(session_data)
        
        return jsonify({
            'success': True,
            'session': diagram_session.to_dict(),
            'has_current_diagram': bool(diagram_session.current_syntax)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('error/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal error: {str(error)}")
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('error/500.html'), 500
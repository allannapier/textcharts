"""
Flask Mermaid Diagram Builder Application
A web application for creating diagrams using natural language and Mermaid.js
"""

from flask import Flask
from config import Config, ProductionConfig
import logging
import os
from typing import Optional

def create_app(config_class: type[Config] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Auto-detect environment and use appropriate config
    if config_class is None:
        if os.environ.get('VERCEL') or os.environ.get('FLASK_ENV') == 'production':
            config_class = ProductionConfig
        else:
            config_class = Config
    
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    from routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    from routes import register_error_handlers
    register_error_handlers(app)
    
    return app


# Create application instance for Vercel
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
Configuration settings for the Flask Mermaid Diagram Builder
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY: str = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL: str = 'gpt-4o-mini'
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 1000
    
    # Application settings
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max file size
    JSON_SORT_KEYS: bool = False
    
    # Mermaid diagram types
    DIAGRAM_TYPES: list[dict[str, str]] = [
        {'value': 'flowchart', 'label': 'Flowchart'},
        {'value': 'sequence', 'label': 'Sequence Diagram'},
        {'value': 'classDiagram', 'label': 'Class Diagram'},
        {'value': 'stateDiagram', 'label': 'State Diagram'},
        {'value': 'erDiagram', 'label': 'Entity Relationship'},
        {'value': 'journey', 'label': 'User Journey'},
        {'value': 'gantt', 'label': 'Gantt Chart'},
        {'value': 'pie', 'label': 'Pie Chart'},
        {'value': 'quadrantChart', 'label': 'Quadrant Chart'},
        {'value': 'mindmap', 'label': 'Mind Map'},
    ]
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG: bool = True
    TESTING: bool = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING: bool = True
    SECRET_KEY: str = 'test-secret-key'
    OPENAI_API_KEY: str = 'test-api-key'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG: bool = False
    TESTING: bool = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
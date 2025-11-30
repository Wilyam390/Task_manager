import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')  # 'sqlite' or 'azure_sql'
    
    # SQLite configuration (local development)
    SQLITE_DATABASE = os.environ.get('SQLITE_DATABASE', 'tasks.db')
    
    # Azure SQL configuration (production)
    AZURE_SQL_SERVER = os.environ.get('AZURE_SQL_SERVER', '')
    AZURE_SQL_DATABASE = os.environ.get('AZURE_SQL_DATABASE', '')
    AZURE_SQL_USERNAME = os.environ.get('AZURE_SQL_USERNAME', '')
    AZURE_SQL_PASSWORD = os.environ.get('AZURE_SQL_PASSWORD', '')
    
    # Azure Application Insights
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get('APPINSIGHTS_INSTRUMENTATION_KEY', '')
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DB_TYPE = 'sqlite'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DB_TYPE = 'azure_sql'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

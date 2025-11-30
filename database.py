"""
Database connection module supporting both SQLite and Azure SQL
"""
import sqlite3
import logging
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Create database connection based on configuration
    Returns a connection object with row_factory set
    """
    config = Config()
    
    if config.DB_TYPE == 'azure_sql':
        return get_azure_sql_connection()
    else:
        return get_sqlite_connection()

def get_sqlite_connection():
    """Create SQLite database connection for local development"""
    try:
        conn = sqlite3.connect(Config.SQLITE_DATABASE)
        conn.row_factory = sqlite3.Row
        logger.info("Connected to SQLite database")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to SQLite: {e}")
        raise

def get_azure_sql_connection():
    """Create Azure SQL database connection for production"""
    try:
        import pyodbc
        
        server = Config.AZURE_SQL_SERVER
        database = Config.AZURE_SQL_DATABASE
        username = Config.AZURE_SQL_USERNAME
        password = Config.AZURE_SQL_PASSWORD
        
        # Connection string for Azure SQL
        connection_string = (
            f'DRIVER={{ODBC Driver 18 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            f'Encrypt=yes;'
            f'TrustServerCertificate=no;'
            f'Connection Timeout=30;'
        )
        
        conn = pyodbc.connect(connection_string)
        logger.info(f"Connected to Azure SQL database: {database}")
        return conn
    except ImportError:
        logger.error("pyodbc not installed. Install with: pip install pyodbc")
        raise
    except Exception as e:
        logger.error(f"Failed to connect to Azure SQL: {e}")
        raise

def init_database():
    """Initialize database schema"""
    conn = get_db_connection()
    
    if Config.DB_TYPE == 'azure_sql':
        init_azure_sql_schema(conn)
    else:
        init_sqlite_schema(conn)
    
    conn.close()
    logger.info("Database initialized successfully")

def init_sqlite_schema(conn):
    """Initialize SQLite schema"""
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()

def init_azure_sql_schema(conn):
    """Initialize Azure SQL schema"""
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
        CREATE TABLE tasks (
            id INT IDENTITY(1,1) PRIMARY KEY,
            title NVARCHAR(255) NOT NULL,
            description NVARCHAR(MAX),
            completed BIT DEFAULT 0,
            created_at DATETIME DEFAULT GETDATE()
        )
    """)
    
    conn.commit()
    cursor.close()

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """
    Execute a database query with automatic connection management
    
    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch_one: Return single row
        fetch_all: Return all rows
    
    Returns:
        Query results or row count
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
        
        return result
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

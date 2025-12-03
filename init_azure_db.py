#!/usr/bin/env python3
"""
Initialize Azure SQL Database with schema
"""
import pyodbc
import sys

# Azure SQL connection details
SERVER = 'task-manager-sql-8b.database.windows.net'
DATABASE = 'taskmanagerdb'
USERNAME = 'sqladmin'
PASSWORD = 'TaskManager2025!'

# Connection string
CONNECTION_STRING = f'Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

# SQL Schema
SCHEMA_SQL = """
-- Drop existing table if it exists
IF OBJECT_ID('tasks', 'U') IS NOT NULL
    DROP TABLE tasks;

-- Create tasks table
CREATE TABLE tasks (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    completed BIT NOT NULL DEFAULT 0,
    due_date DATETIME2 NULL,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Insert sample data
INSERT INTO tasks (title, completed) VALUES
    ('Welcome to Task Manager on Azure!', 0),
    ('Configure Azure DevOps Pipeline', 0),
    ('Deploy to Production', 0);
"""

def init_database():
    """Initialize the Azure SQL database"""
    print("🗄️  Initializing Azure SQL Database...")
    print(f"Server: {SERVER}")
    print(f"Database: {DATABASE}")
    print("")
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        conn = pyodbc.connect(CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Execute schema
        print("📝 Creating schema...")
        for statement in SCHEMA_SQL.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        conn.commit()
        
        # Verify
        print("✅ Verifying setup...")
        cursor.execute("SELECT COUNT(*) as count FROM tasks")
        count = cursor.fetchone()[0]
        print(f"   Tasks in database: {count}")
        
        cursor.execute("SELECT title FROM tasks")
        print("\n📋 Sample tasks:")
        for row in cursor.fetchall():
            print(f"   - {row[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure ODBC Driver 18 for SQL Server is installed")
        print("2. Check firewall rules allow your IP")
        print("3. Verify credentials are correct")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

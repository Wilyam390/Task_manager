import sqlite3
import os

DATABASE = 'tasks.db'

def init_db():
    """Initialize the database with schema"""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
        print(f"Removed existing {DATABASE}")
    
    conn = sqlite3.connect(DATABASE)
    
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (title, description, completed, due_date) 
        VALUES ('Sample Task', 'This is a sample task', 0, datetime('now', '+1 day'))
    """)
    cursor.execute("""
        INSERT INTO tasks (title, description, completed, due_date) 
        VALUES ('Completed Task', 'This task is done', 1, datetime('now'))
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database {DATABASE} initialized successfully")

if __name__ == '__main__':
    init_db()

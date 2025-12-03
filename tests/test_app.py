import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    """Create test client with fresh database"""
    app.config['TESTING'] = True
    
    import sqlite3
    # Initialize database with schema
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0,
            due_date DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Clear existing data and insert test data
    cursor.execute('DELETE FROM tasks')
    cursor.execute("INSERT INTO tasks (title, completed) VALUES ('Test Task', 0)")
    conn.commit()
    conn.close()
    
    with app.test_client() as client:
        yield client

def test_home_page_loads(client):
    """Test that homepage loads"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Task Manager' in response.data

def test_home_displays_tasks(client):
    """Test that homepage displays tasks"""
    response = client.get('/')
    assert b'Test Task' in response.data

def test_add_task_success(client):
    """Test adding a valid task"""
    response = client.post('/task/add', data={
        'title': 'New Task'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'New Task' in response.data

def test_add_task_no_title(client):
    """Test that empty title is rejected"""
    response = client.post('/task/add', data={
        'title': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should show an error message or stay on same page

def test_toggle_task(client):
    """Test toggling task completion"""
    # Get the task ID that was created in the fixture
    import sqlite3
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM tasks LIMIT 1')
    task_id = cursor.fetchone()[0]
    conn.close()
    
    response = client.post(f'/task/{task_id}/toggle', follow_redirects=True)
    assert response.status_code == 200

def test_delete_task(client):
    """Test deleting a task"""
    # Get the task ID that was created in the fixture
    import sqlite3
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM tasks LIMIT 1')
    task_id = cursor.fetchone()[0]
    conn.close()
    
    response = client.post(f'/task/{task_id}/delete', follow_redirects=True)
    assert response.status_code == 200

def test_health_endpoint(client):
    """Test health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

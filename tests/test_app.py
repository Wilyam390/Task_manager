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
    conn = sqlite3.connect('tasks.db')
    conn.execute('DELETE FROM tasks')
    conn.execute("INSERT INTO tasks (id, title, description, completed) VALUES (1, 'Test Task', 'Test description', 0)")
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
        'title': 'New Task',
        'description': 'New description'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Task created successfully' in response.data

def test_add_task_no_title(client):
    """Test that empty title is rejected"""
    response = client.post('/task/add', data={
        'title': '',
        'description': 'Test'
    }, follow_redirects=True)
    
    assert b'required' in response.data.lower()

def test_toggle_task(client):
    """Test toggling task completion"""
    response = client.post('/task/1/toggle', follow_redirects=True)
    assert response.status_code == 200
    assert b'Task status updated' in response.data

def test_delete_task(client):
    """Test deleting a task"""
    response = client.post('/task/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'deleted successfully' in response.data.lower()

def test_health_endpoint(client):
    """Test health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
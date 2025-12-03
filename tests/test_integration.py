"""
Integration tests for Task Manager application
Tests complete workflows and end-to-end functionality
"""
import pytest
import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    """Create test client with fresh database"""
    app.config['TESTING'] = True
    
    # Initialize database with schema
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('DELETE FROM tasks')
    conn.commit()
    conn.close()
    
    with app.test_client() as client:
        yield client

def test_complete_task_lifecycle(client):
    """Test creating, toggling, and deleting a task"""
    # Create a task
    response = client.post('/task/add', data={'title': 'Integration Test Task'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Integration Test Task' in response.data
    
    # Get the task ID
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM tasks WHERE title = ?', ('Integration Test Task',))
    task_id = cursor.fetchone()[0]
    conn.close()
    
    # Toggle the task
    response = client.post(f'/task/{task_id}/toggle', follow_redirects=True)
    assert response.status_code == 200
    
    # Verify it's completed
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
    completed = cursor.fetchone()[0]
    conn.close()
    assert completed == 1
    
    # Delete the task
    response = client.post(f'/task/{task_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Integration Test Task' not in response.data

def test_multiple_tasks_creation(client):
    """Test creating multiple tasks"""
    tasks = ['Task 1', 'Task 2', 'Task 3']
    
    for task_title in tasks:
        response = client.post('/task/add', data={'title': task_title}, follow_redirects=True)
        assert response.status_code == 200
    
    # Verify all tasks are displayed
    response = client.get('/')
    for task_title in tasks:
        assert task_title.encode() in response.data

def test_task_validation(client):
    """Test input validation"""
    # Empty title
    response = client.post('/task/add', data={'title': ''}, follow_redirects=True)
    assert response.status_code == 200
    
    # Very long title (over 255 characters)
    long_title = 'A' * 300
    response = client.post('/task/add', data={'title': long_title}, follow_redirects=True)
    assert response.status_code == 200
    assert b'too long' in response.data or b'required' in response.data

def test_toggle_nonexistent_task(client):
    """Test toggling a task that doesn't exist"""
    response = client.post('/task/99999/toggle', follow_redirects=True)
    assert response.status_code == 200

def test_delete_nonexistent_task(client):
    """Test deleting a task that doesn't exist"""
    response = client.post('/task/99999/delete', follow_redirects=True)
    assert response.status_code == 200

def test_health_endpoint_with_tasks(client):
    """Test health endpoint with tasks in database"""
    # Add some tasks
    client.post('/task/add', data={'title': 'Health Test Task'}, follow_redirects=True)
    
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['tasks_count'] >= 1

def test_task_persistence(client):
    """Test that tasks persist across requests"""
    # Create a task
    client.post('/task/add', data={'title': 'Persistent Task'}, follow_redirects=True)
    
    # Make a new request to verify it's still there
    response = client.get('/')
    assert b'Persistent Task' in response.data

def test_task_ordering(client):
    """Test that tasks are ordered by creation time (newest first)"""
    # Create tasks in sequence
    client.post('/task/add', data={'title': 'First Task'}, follow_redirects=True)
    client.post('/task/add', data={'title': 'Second Task'}, follow_redirects=True)
    client.post('/task/add', data={'title': 'Third Task'}, follow_redirects=True)
    
    response = client.get('/')
    content = response.data.decode()
    
    # Third Task should appear before First Task
    third_pos = content.find('Third Task')
    first_pos = content.find('First Task')
    assert third_pos < first_pos

def test_toggle_task_twice(client):
    """Test toggling a task twice returns to original state"""
    # Create a task
    client.post('/task/add', data={'title': 'Toggle Test'}, follow_redirects=True)
    
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, completed FROM tasks WHERE title = ?', ('Toggle Test',))
    task_id, initial_status = cursor.fetchone()
    conn.close()
    
    # Toggle once
    client.post(f'/task/{task_id}/toggle', follow_redirects=True)
    
    # Toggle twice
    client.post(f'/task/{task_id}/toggle', follow_redirects=True)
    
    # Check final status matches initial
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,))
    final_status = cursor.fetchone()[0]
    conn.close()
    
    assert initial_status == final_status

def test_error_handlers(client):
    """Test custom error handlers"""
    # Test 404 handler
    response = client.get('/nonexistent-route')
    assert response.status_code == 404

def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint"""
    response = client.get('/metrics')
    # Should return metrics or error if prometheus not available
    assert response.status_code in [200, 503]

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-later'

DATABASE = 'tasks.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Display all tasks"""
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/task/add', methods=['POST'])
def add_task():
    """Create a new task"""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()

    if not title:
        flash('Task title is required', 'error')
        return redirect(url_for('home'))
    
    if len(title) > 255:
        flash('Task title too long (max 255 characters)', 'error')
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tasks (title, description) VALUES (?, ?)',
        (title, description)
    )
    conn.commit()
    conn.close()
    
    flash('Task created successfully', 'success')
    return redirect(url_for('home'))

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Toggle task completion status"""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    
    if task:
        new_status = 0 if task['completed'] else 1
        conn.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
        flash('Task status updated', 'success')
    else:
        flash('Task not found', 'error')
    
    conn.close()
    return redirect(url_for('home'))

@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task"""
    conn = get_db_connection()
    result = conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    
    if result.rowcount > 0:
        flash('Task deleted successfully', 'success')
    else:
        flash('Task not found', 'error')
    
    conn.close()
    return redirect(url_for('home'))

@app.route('/health')
def health():
    """Health check endpoint"""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    conn.close()
    return {'status': 'healthy', 'tasks_count': count}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
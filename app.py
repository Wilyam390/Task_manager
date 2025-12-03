import logging
import sys
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response

from config import config, Config
from database import get_db_connection

# Prometheus metrics (optional)
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

    PROMETHEUS_AVAILABLE = True
    REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
    TASK_OPERATIONS = Counter('task_operations_total', 'Total task operations', ['operation'])
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = Config.ENVIRONMENT
app.config.from_object(config.get(env, config['default']))
app.secret_key = app.config['SECRET_KEY']


def ensure_due_date_column():
    """Add due_date column if it is missing (helps older DBs)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if app.config['DB_TYPE'] == 'azure_sql':
            cursor.execute(
                "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='tasks' AND COLUMN_NAME='due_date'"
            )
            exists = cursor.fetchone()
            if not exists:
                cursor.execute("ALTER TABLE tasks ADD due_date DATETIME NULL")
                conn.commit()
                logger.info("Added due_date column to Azure SQL tasks table")
        else:
            cursor.execute("PRAGMA table_info(tasks)")
            columns = []
            for row in cursor.fetchall():
                try:
                    columns.append(row['name'])
                except Exception:
                    columns.append(row[1] if len(row) > 1 else row[0])
            if 'due_date' not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN due_date DATETIME")
                conn.commit()
                logger.info("Added due_date column to SQLite tasks table")
    except Exception as exc:
        logger.warning("Could not ensure due_date column exists: %s", exc)
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass


def parse_datetime_value(value):
    """Return datetime from DB value or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def row_to_dict(row, columns):
    """Normalize DB row to dict for both SQLite and Azure SQL."""
    try:
        return dict(row)
    except Exception:
        return {col: row[idx] for idx, col in enumerate(columns)}


def fetch_tasks():
    """Fetch tasks and annotate with derived flags."""
    ensure_due_date_column()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, description, completed, created_at, due_date FROM tasks ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    column_names = [col[0] for col in cursor.description] if cursor.description else []

    tasks = []
    now = datetime.now()
    for row in rows:
        raw = row_to_dict(row, column_names)
        created_at = parse_datetime_value(raw.get('created_at'))
        due_date = parse_datetime_value(raw.get('due_date'))

        task = {
            'id': raw.get('id'),
            'title': raw.get('title', ''),
            'description': raw.get('description', ''),
            'completed': bool(raw.get('completed')),
            'created_at': created_at,
            'due_date': due_date
        }
        task['is_overdue'] = (not task['completed']) and task['due_date'] is not None and task['due_date'] < now
        task['is_due_today'] = task['due_date'] is not None and task['due_date'].date() == now.date()
        tasks.append(task)

    cursor.close()
    conn.close()
    return tasks


# Middleware to track metrics (if installed)
if PROMETHEUS_AVAILABLE:
    @app.before_request
    def before_request():
        request.start_time = datetime.now()

    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            latency = (datetime.now() - request.start_time).total_seconds()
            REQUEST_LATENCY.labels(method=request.method, endpoint=request.endpoint or 'unknown').observe(latency)
            REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint or 'unknown',
                                 status=response.status_code).inc()
        return response


@app.route('/')
def home():
    """Display all tasks with filtering, search, and sorting."""
    try:
        tasks = fetch_tasks()

        search_term = request.args.get('q', '').strip().lower()
        status_filter = request.args.get('status', 'all')
        sort_option = request.args.get('sort', 'created_desc')

        filtered = []
        for task in tasks:
            if search_term and search_term not in task['title'].lower():
                continue

            if status_filter == 'completed' and not task['completed']:
                continue
            if status_filter == 'pending' and task['completed']:
                continue
            if status_filter == 'overdue' and not task['is_overdue']:
                continue
            if status_filter == 'today':
                if not task['due_date'] or task['due_date'].date() != datetime.now().date():
                    continue

            filtered.append(task)

        reverse = True if sort_option == 'created_desc' else False
        filtered.sort(key=lambda t: t['created_at'] or datetime.min, reverse=reverse)

        filters = {
            'q': search_term,
            'status': status_filter,
            'sort': sort_option
        }

        logger.info("Rendering %d tasks after filters", len(filtered))
        return render_template('index.html', tasks=filtered, filters=filters)
    except Exception as exc:
        logger.error("Error fetching tasks: %s", exc)
        flash('Error loading tasks', 'error')
        return render_template('index.html', tasks=[], filters={})


@app.route('/task/add', methods=['POST'])
def add_task():
    """Create a new task."""
    try:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        due_date_str = request.form.get('due_date', '').strip()

        if not title:
            logger.warning("Task creation attempted without title")
            flash('Task title is required', 'error')
            return redirect(url_for('home'))

        if len(title) > 255:
            logger.warning("Task title too long: %d characters", len(title))
            flash('Task title too long (max 255 characters)', 'error')
            return redirect(url_for('home'))

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash('Invalid due date format', 'error')
                return redirect(url_for('home'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)',
            (title, description, due_date.isoformat() if due_date else None)
        )
        conn.commit()
        cursor.close()
        conn.close()

        if PROMETHEUS_AVAILABLE:
            TASK_OPERATIONS.labels(operation='create').inc()

        logger.info("Task created: %s", title)
        flash('Task created successfully', 'success')
        return redirect(url_for('home'))
    except Exception as exc:
        logger.error("Error creating task: %s", exc)
        flash('Error creating task', 'error')
        return redirect(url_for('home'))


@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Toggle task completion status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, completed FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()

        if not row:
            flash('Task not found', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('home'))

        columns = [col[0] for col in cursor.description]
        task = row_to_dict(row, columns)
        new_status = 0 if task.get('completed') else 1

        cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
        cursor.close()
        conn.close()

        if PROMETHEUS_AVAILABLE:
            TASK_OPERATIONS.labels(operation='toggle').inc()

        logger.info("Task %s status toggled to %s", task_id, new_status)
        flash('Task status updated', 'success')
        return redirect(url_for('home'))
    except Exception as exc:
        logger.error("Error toggling task %s: %s", task_id, exc)
        flash('Error updating task', 'error')
        return redirect(url_for('home'))


@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()

        if cursor.rowcount > 0:
            if PROMETHEUS_AVAILABLE:
                TASK_OPERATIONS.labels(operation='delete').inc()

            logger.info("Task %s deleted", task_id)
            flash('Task deleted successfully', 'success')
        else:
            logger.warning("Task %s not found for deletion", task_id)
            flash('Task not found', 'error')

        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    except Exception as exc:
        logger.error("Error deleting task %s: %s", task_id, exc)
        flash('Error deleting task', 'error')
        return redirect(url_for('home'))


@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tasks')
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        response = {
            'status': 'healthy',
            'tasks_count': count,
            'environment': app.config['ENVIRONMENT'],
            'database': app.config['DB_TYPE']
        }
        logger.info("Health check passed")
        return jsonify(response), 200
    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        return jsonify({'status': 'unhealthy', 'error': str(exc)}), 500


@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    if PROMETHEUS_AVAILABLE:
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    return jsonify({'error': 'Prometheus client not installed'}), 503


# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning("404 error: %s", request.url)
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("500 error: %s", error)
    return render_template('errors/500.html'), 500


@app.errorhandler(Exception)
def handle_exception(exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    logger.info("Starting Flask application")
    port = 8000 if app.config['DEBUG'] else 80
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

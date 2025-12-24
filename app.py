"""
Deadline Assign AI - Main Flask Application
A smart system for deadline assignment and task management

Author: Angad05-hub
Created: 2025-12-24
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///deadlineai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== Database Models ====================

class User(db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')  # user, manager, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='assignee', lazy=True, foreign_keys='Task.assigned_to')
    created_tasks = db.relationship('Task', backref='creator', lazy=True, foreign_keys='Task.created_by')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)


class Task(db.Model):
    """Task model for deadline management"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False, index=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, overdue
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.String(200))  # comma-separated
    estimated_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat(),
            'priority': self.priority,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'category': self.category,
            'tags': self.tags,
            'estimated_hours': self.estimated_hours,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Notification(db.Model):
    """Notification model for user alerts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # deadline_warning, task_assigned, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='notifications')
    task = db.relationship('Task', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}>'


# ==================== Login Manager ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== Routes - Authentication ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Deadline Assign AI'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        # TODO: Implement password verification
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_active:
            login_user(user)
            logger.info(f'User {username} logged in successfully')
            if request.is_json:
                return jsonify({'success': True, 'message': 'Login successful'}), 200
            return redirect(url_for('dashboard'))
        
        logger.warning(f'Failed login attempt for username: {username}')
        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f'User {username} logged out')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        
        # Validation
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # TODO: Hash password properly
        user = User(
            username=username,
            email=email,
            password_hash=password,  # Replace with hashed password
            full_name=full_name
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f'New user registered: {username}')
            return jsonify({'success': True, 'message': 'Registration successful'}), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f'Registration error: {str(e)}')
            return jsonify({'success': False, 'message': 'Registration failed'}), 500
    
    return render_template('register.html')


# ==================== Routes - Dashboard ====================

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')


# ==================== Routes - Tasks API ====================

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks for current user"""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        query = Task.query.filter(
            (Task.assigned_to == current_user.id) | (Task.created_by == current_user.id)
        )
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        
        tasks = query.all()
        return jsonify([task.to_dict() for task in tasks]), 200
    except Exception as e:
        logger.error(f'Error fetching tasks: {str(e)}')
        return jsonify({'error': 'Failed to fetch tasks'}), 500


@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('title') or not data.get('deadline'):
            return jsonify({'error': 'Title and deadline are required'}), 400
        
        task = Task(
            title=data.get('title'),
            description=data.get('description', ''),
            deadline=datetime.fromisoformat(data.get('deadline')),
            priority=data.get('priority', 'medium'),
            category=data.get('category'),
            tags=data.get('tags', ''),
            estimated_hours=data.get('estimated_hours'),
            created_by=current_user.id,
            assigned_to=data.get('assigned_to')
        )
        
        db.session.add(task)
        db.session.commit()
        logger.info(f'Task created: {task.id} by {current_user.username}')
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating task: {str(e)}')
        return jsonify({'error': 'Failed to create task'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get a specific task"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.assigned_to != current_user.id and task.created_by != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(task.to_dict()), 200
    except Exception as e:
        logger.error(f'Error fetching task {task_id}: {str(e)}')
        return jsonify({'error': 'Task not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update a task"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.created_by != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'deadline' in data:
            task.deadline = datetime.fromisoformat(data['deadline'])
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
        if 'assigned_to' in data:
            task.assigned_to = data['assigned_to']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        logger.info(f'Task updated: {task_id}')
        return jsonify(task.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating task {task_id}: {str(e)}')
        return jsonify({'error': 'Failed to update task'}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # Check authorization
        if task.created_by != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(task)
        db.session.commit()
        logger.info(f'Task deleted: {task_id}')
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting task {task_id}: {str(e)}')
        return jsonify({'error': 'Failed to delete task'}), 500


# ==================== Routes - Notifications ====================

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get user notifications"""
    try:
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()
        ).all()
        
        return jsonify([{
            'id': n.id,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        } for n in notifications]), 200
    except Exception as e:
        logger.error(f'Error fetching notifications: {str(e)}')
        return jsonify({'error': 'Failed to fetch notifications'}), 500


@app.route('/api/notifications/<int:notification_id>', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating notification: {str(e)}')
        return jsonify({'error': 'Failed to update notification'}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f'Internal server error: {str(error)}')
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    return jsonify({'error': 'Access forbidden'}), 403


# ==================== Initialize Database ====================

@app.before_first_request
def create_tables():
    """Create database tables"""
    db.create_all()
    logger.info('Database tables created')


# ==================== Main ====================

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Run development server
    debug_mode = os.getenv('FLASK_DEBUG', False)
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f'Starting Deadline Assign AI server on port {port}')
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

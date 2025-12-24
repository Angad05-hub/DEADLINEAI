"""
Configuration settings for DEADLINEAI application.
Last updated: 2025-12-24 14:15:16 (UTC)
"""

import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Environment settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = ENVIRONMENT == 'development'

# Application metadata
APP_NAME = 'DEADLINEAI'
APP_VERSION = '1.0.0'
APP_DESCRIPTION = 'AI-powered deadline and task management application'

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///deadlineai.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# API configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
API_DEBUG = DEBUG

# Authentication settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')

# Deadline AI settings
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 2000))

# Task configuration
MAX_TASKS_PER_USER = int(os.getenv('MAX_TASKS_PER_USER', 100))
TASK_REMINDER_HOURS_BEFORE = int(os.getenv('TASK_REMINDER_HOURS_BEFORE', 24))

# File upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10485760))  # 10MB in bytes
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# Cache configuration
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'noreply@deadlineai.com')

# Pagination
ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 20))

# CORS settings
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

# Feature flags
ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
ENABLE_EMAIL_REMINDERS = os.getenv('ENABLE_EMAIL_REMINDERS', 'true').lower() == 'true'
ENABLE_AI_SUGGESTIONS = os.getenv('ENABLE_AI_SUGGESTIONS', 'true').lower() == 'true'

# Session configuration
SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT_MINUTES * 60

# Additional settings
TIMEZONE = os.getenv('TIMEZONE', 'UTC')
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'ja', 'zh']
DEFAULT_LANGUAGE = 'en'

# Performance settings
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', 20))

# Rate limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', 60))

def get_config():
    """Return the current configuration dictionary."""
    return {
        'debug': DEBUG,
        'environment': ENVIRONMENT,
        'database_url': DATABASE_URL,
        'api_host': API_HOST,
        'api_port': API_PORT,
        'log_level': LOG_LEVEL,
        'ai_model': AI_MODEL,
    }

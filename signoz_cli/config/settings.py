from pathlib import Path

# Configuration paths
CONFIG_DIR = Path.home() / '.config' / 'signoz'
CONFIG_FILE = CONFIG_DIR / 'config.json'

# API defaults
DEFAULT_API_URL = 'http://localhost:3301'
API_VERSION = 'v1'

# API endpoints
ENDPOINTS = {
    'login': f'/api/{API_VERSION}/login',
    'dashboards': f'/api/{API_VERSION}/dashboards'
} 
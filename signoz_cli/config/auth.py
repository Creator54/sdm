import json
import os
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

from .settings import CONFIG_DIR, CONFIG_FILE

class TokenManager:
    @staticmethod
    def save_token(token: str, email: str, api_url: str) -> None:
        """Save token and related info to config file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = {
            'token': token,
            'email': email,
            'api_url': api_url,
            'last_login': datetime.now().isoformat()
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        # Secure the config file
        os.chmod(CONFIG_FILE, 0o600)

    @staticmethod
    def load_token() -> Optional[str]:
        """Load token from config file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('token')
        return None

    @staticmethod
    def load_api_url() -> Optional[str]:
        """Load API URL from config file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('api_url')
        return None

    @staticmethod
    def get_config() -> Dict:
        """Get full configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {} 
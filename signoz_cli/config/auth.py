import json
import os
from datetime import datetime
from typing import Optional, Dict

from .settings import CONFIG_DIR, CONFIG_FILE

class TokenManager:
    @staticmethod
    def load_token() -> Optional[str]:
        """Load token from config file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
                    return config.get('token')
            except (json.JSONDecodeError, IOError):
                return None
        return None

    @staticmethod
    def save_token(token: str, email: str) -> None:
        """Save token and email to config file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = {
            'token': token,
            'email': email,
            'last_login': datetime.now().isoformat()
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        # Secure the config file
        os.chmod(CONFIG_FILE, 0o600)

    @staticmethod
    def get_config() -> Dict:
        """Get current configuration"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {} 
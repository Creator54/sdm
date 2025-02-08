import json
import os
from typing import Optional, Tuple, Dict, List
import requests

from ..config.settings import DEFAULT_API_URL, ENDPOINTS
from ..config.auth import TokenManager

class SignozAPI:
    def __init__(self, base_url: str = DEFAULT_API_URL, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.token = token or TokenManager.load_token()
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}' if self.token else None
        }

    @staticmethod
    def login(base_url: str, email: Optional[str] = None, password: Optional[str] = None) -> Tuple[bool, str]:
        """Login to SigNoz and get JWT token"""
        # Use environment variables if email/password not provided
        email = email or os.environ.get('SIGNOZ_EMAIL')
        password = password or os.environ.get('SIGNOZ_PASSWORD')
        
        if not email or not password:
            return False, "Email and password are required. Set them in .env file or provide via command line."
        
        url = f"{base_url.rstrip('/')}{ENDPOINTS['login']}"
        
        try:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={'email': email, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'accessJwt' in data:
                    TokenManager.save_token(data['accessJwt'], email)
                    return True, data['accessJwt']
                return False, "No access token in response"
            else:
                return False, f"Login failed: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def list_dashboards(self) -> List[Dict]:
        """List all available dashboards"""
        response = requests.get(
            f"{self.base_url}{ENDPOINTS['dashboards']}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json().get('data', [])
        raise Exception(f"Error listing dashboards: {response.status_code} - {response.text}")

    def delete_dashboard(self, uuid: str) -> bool:
        """Delete a dashboard by UUID"""
        response = requests.delete(
            f"{self.base_url}{ENDPOINTS['dashboards']}/{uuid}",
            headers=self.headers
        )
        
        if response.status_code in [200, 204]:
            return True
        raise Exception(f"Error deleting dashboard: {response.status_code} - {response.text}")

    def add_dashboard(self, dashboard_data: Dict) -> str:
        """Add a new dashboard"""
        response = requests.post(
            f"{self.base_url}{ENDPOINTS['dashboards']}",
            headers=self.headers,
            json=dashboard_data
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('status') == 'success' and 'data' in data:
                return str(data['data'].get('id', 'Unknown'))
            return 'Unknown'
        raise Exception(f"Error adding dashboard: {response.status_code} - {response.text}") 
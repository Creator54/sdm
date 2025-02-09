import json
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
import requests
from jwt import decode, InvalidTokenError

from ..config.settings import DEFAULT_API_URL, ENDPOINTS
from ..config.auth import TokenManager

class SignozAPI:
    def __init__(self, base_url: str = DEFAULT_API_URL, token: Optional[str] = None):
        # Use provided URL, or load from config, or fallback to default
        saved_url = TokenManager.load_api_url()
        # Only use default if no URL is provided and none is saved
        self.base_url = base_url if base_url != DEFAULT_API_URL else (saved_url or DEFAULT_API_URL)
        self.base_url = self.base_url.rstrip('/')
        
        # Debug print to check URL being used
        print(f"Debug: Using API URL: {self.base_url}")
        print(f"Debug: Saved URL: {saved_url}")
        print(f"Debug: Provided URL: {base_url}")
        
        self.token = token or TokenManager.load_token()
        if self.token and not self._is_token_valid(self.token):
            self.token = None
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}' if self.token else None
        }

    @staticmethod
    def _is_token_valid(token: str) -> bool:
        """Check if token is valid and not expired"""
        try:
            # JWT tokens can be decoded without verification to check expiration
            decoded = decode(token, options={"verify_signature": False})
            exp = decoded.get('exp')
            if exp:
                # Add 5 minutes buffer
                return datetime.fromtimestamp(exp) > datetime.now() + timedelta(minutes=5)
            return True
        except InvalidTokenError:
            return False

    def _handle_response(self, response: requests.Response, error_prefix: str) -> Dict:
        """Handle API response and provide meaningful error messages"""
        try:
            data = response.json()
            if response.status_code >= 400:
                error_msg = data.get('error', data.get('message', 'Unknown error'))
                error_type = data.get('errorType', 'error')
                raise Exception(f"{error_prefix}: {response.status_code} - [{error_type}] {error_msg}")
            return data
        except json.JSONDecodeError:
            raise Exception(f"{error_prefix}: Invalid JSON response from server")
        except requests.exceptions.RequestException as e:
            raise Exception(f"{error_prefix}: Request failed - {str(e)}")

    @staticmethod
    def login(base_url: str, email: Optional[str] = None, password: Optional[str] = None) -> Tuple[bool, str]:
        """Login to SigNoz and get JWT token"""
        email = email or os.environ.get('SIGNOZ_EMAIL')
        password = password or os.environ.get('SIGNOZ_PASSWORD')
        
        if not email or not password:
            return False, "Email and password are required. Set them in .env file or provide via command line."
        
        # Ensure we're using the provided URL, not the default
        base_url = base_url if base_url != DEFAULT_API_URL else TokenManager.load_api_url() or DEFAULT_API_URL
        url = f"{base_url.rstrip('/')}{ENDPOINTS['login']}"
        
        print(f"Debug: Login URL: {url}")  # Debug print
        
        try:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json'},
                json={'email': email, 'password': password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'accessJwt' in data:
                    # Save the actual URL used for login
                    TokenManager.save_token(data['accessJwt'], email, base_url)
                    return True, data['accessJwt']
                return False, "No access token in response"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', error_data.get('message', 'Unknown error'))
                    return False, f"Login failed: {response.status_code} - {error_msg}"
                except json.JSONDecodeError:
                    return False, f"Login failed: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def list_dashboards(self) -> List[Dict]:
        """List all available dashboards"""
        try:
            response = requests.get(
                f"{self.base_url}{ENDPOINTS['dashboards']}",
                headers=self.headers
            )
            data = self._handle_response(response, "Error listing dashboards")
            return data.get('data', [])
        except Exception as e:
            raise Exception(f"Failed to list dashboards: {str(e)}")

    def delete_dashboard(self, uuid: str) -> bool:
        """Delete a dashboard by UUID"""
        try:
            response = requests.delete(
                f"{self.base_url}{ENDPOINTS['dashboards']}/{uuid}",
                headers=self.headers
            )
            if response.status_code in [200, 204]:
                return True
            self._handle_response(response, "Error deleting dashboard")
            return False
        except Exception as e:
            raise Exception(f"Failed to delete dashboard: {str(e)}")

    def add_dashboard(self, dashboard_data: Dict) -> str:
        """Add a new dashboard"""
        try:
            response = requests.post(
                f"{self.base_url}{ENDPOINTS['dashboards']}",
                headers=self.headers,
                json=dashboard_data
            )
            data = self._handle_response(response, "Error adding dashboard")
            if data.get('status') == 'success' and 'data' in data:
                # Extract UUID from the response data
                uuid = data['data'].get('uuid', data['data'].get('id', 'Unknown'))
                return str(uuid)
            raise Exception("Invalid response format from server")
        except Exception as e:
            raise Exception(f"Failed to add dashboard: {str(e)}") 
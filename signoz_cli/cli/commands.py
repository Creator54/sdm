import json
import sys
from typing import Optional, List
import requests
from urllib.parse import urlparse

from ..api.client import SignozAPI
from ..config.auth import TokenManager
from ..config.settings import CONFIG_FILE
from .ui import UI

class Commands:
    @staticmethod
    def login(api: SignozAPI, email: Optional[str], password: Optional[str]) -> None:
        """Handle login command"""
        with UI.progress_context("Logging in...") as progress:
            task = progress.add_task("Authenticating...", total=None)
            success, result = api.login(api.base_url, email, password)
            progress.remove_task(task)

        if success:
            UI.print_success("Login successful!")
            UI.print_info(f"Token saved to {CONFIG_FILE}")
            UI.print_info("You can now use other commands without providing the token")
        else:
            UI.print_error(f"Login failed: {result}")
            sys.exit(1)

    @staticmethod
    def show_config() -> None:
        """Handle config command"""
        config = TokenManager.get_config()
        config['config_location'] = CONFIG_FILE
        UI.display_config(config)

    @staticmethod
    def list_dashboards(api: SignozAPI) -> None:
        """Handle list command"""
        try:
            with UI.progress_context("Fetching dashboards...") as progress:
                task = progress.add_task("Loading...", total=None)
                dashboards = api.list_dashboards()
                progress.remove_task(task)
            
            UI.display_dashboards(dashboards)
        except Exception as e:
            UI.print_error(str(e))
            sys.exit(1)

    @staticmethod
    def delete_dashboards(api: SignozAPI, identifiers: List[str], force: bool = False, by_title: bool = False) -> None:
        """Handle delete command for multiple dashboards"""
        try:
            # First, get all dashboards to match against titles if needed
            all_dashboards = api.list_dashboards() if by_title else []
            
            # Collect UUIDs to delete
            uuids_to_delete = []
            if by_title:
                import re
                for pattern in identifiers:
                    try:
                        regex = re.compile(pattern, re.IGNORECASE)
                        matches = [
                            dashboard['uuid'] for dashboard in all_dashboards
                            if regex.search(dashboard.get('data', {}).get('title', ''))
                        ]
                        if matches:
                            uuids_to_delete.extend(matches)
                        else:
                            UI.print_warning(f"No dashboards found matching pattern: {pattern}")
                    except re.error as e:
                        UI.print_error(f"Invalid regex pattern '{pattern}': {str(e)}")
                        if not force:
                            return
            else:
                uuids_to_delete = identifiers

            # Remove duplicate UUIDs while preserving order
            unique_uuids = list(dict.fromkeys(uuids_to_delete))
            if len(unique_uuids) < len(uuids_to_delete):
                UI.print_warning(f"Found {len(uuids_to_delete) - len(unique_uuids)} duplicate dashboard UUIDs. Will process only unique UUIDs.")
            
            if not unique_uuids:
                UI.print_warning("No dashboards found to delete")
                return

            total = len(unique_uuids)
            
            # Show matched dashboards before deletion
            if by_title and not force:
                UI.print_info("Matched dashboards to delete:")
                matched_dashboards = [
                    dashboard for dashboard in all_dashboards
                    if dashboard['uuid'] in unique_uuids
                ]
                for dashboard in matched_dashboards:
                    UI.print_info(f"  - {dashboard.get('data', {}).get('title', 'Untitled')} ({dashboard['uuid']})")
            
            # Single confirmation if not force mode
            if not force:
                message = f"Are you sure you want to delete {total} dashboard{'s' if total > 1 else ''}?"
                if not UI.confirm_action(message):
                    UI.print_info("Operation cancelled")
                    return

            success_count = 0
            failed_uuids = []
            
            # Perform the deletions with progress bar
            with UI.progress_context("Deleting dashboards...") as progress:
                task_id = progress.add_task("Processing...", total=total)
                
                for i, uuid in enumerate(unique_uuids, 1):
                    try:
                        progress.update(task_id, description=f"Deleting {uuid} ({i}/{total})")
                        if api.delete_dashboard(uuid):
                            success_count += 1
                            UI.print_success(f"Deleted dashboard: {uuid}")
                    except Exception as e:
                        UI.print_error(f"Failed to delete dashboard {uuid}: {str(e)}")
                        failed_uuids.append(uuid)
                    progress.update(task_id, advance=1)

            # Summary
            if failed_uuids:
                UI.print_warning(
                    f"Deleted {success_count} of {total} dashboard{'s' if total > 1 else ''}"
                    f". Failed: {', '.join(failed_uuids)}"
                )
            else:
                UI.print_success(f"Successfully deleted {success_count} dashboard{'s' if success_count > 1 else ''}")
        except Exception as e:
            UI.print_error(str(e))
            sys.exit(1)

    @staticmethod
    def _load_json_from_url(url: str) -> dict:
        """Load JSON data from a URL"""
        try:
            # Handle GitHub URLs - convert to raw content if needed
            parsed_url = urlparse(url)
            if parsed_url.netloc == 'github.com':
                # Convert github.com URL to raw.githubusercontent.com
                path_parts = parsed_url.path.split('/')
                if len(path_parts) >= 5 and path_parts[3] == 'blob':
                    # Remove 'blob' from path
                    path_parts.pop(3)
                    raw_url = f"https://raw.githubusercontent.com{'/'.join(path_parts)}"
                    url = raw_url

            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch JSON from URL: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON data in URL response")

    @staticmethod
    def _load_json_from_file(file_path: str) -> dict:
        """Load JSON data from a local file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Dashboard file not found: {file_path}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in dashboard file: {file_path}")

    @staticmethod
    def add_dashboards(api: SignozAPI, file_paths: List[str], skip_errors: bool = False, force: bool = False) -> None:
        """Handle add command for multiple dashboards"""
        try:
            total = len(file_paths)
            
            # Single confirmation if not force mode
            if not force and total > 1:
                message = f"Are you sure you want to add {total} dashboards?"
                if not UI.confirm_action(message):
                    UI.print_info("Operation cancelled")
                    return
            
            success_count = 0
            failed_paths = []
            
            with UI.progress_context("Adding dashboards...") as progress:
                task_id = progress.add_task("Processing...", total=total)
                
                for i, file_path in enumerate(file_paths, 1):
                    try:
                        # Check if input is a URL or local file
                        parsed = urlparse(file_path)
                        if parsed.scheme in ('http', 'https'):
                            progress.update(task_id, description=f"Fetching from URL: {file_path} ({i}/{total})")
                            dashboard_data = Commands._load_json_from_url(file_path)
                        else:
                            progress.update(task_id, description=f"Loading file: {file_path} ({i}/{total})")
                            dashboard_data = Commands._load_json_from_file(file_path)
                        
                        progress.update(task_id, description=f"Uploading dashboard from {file_path} ({i}/{total})")
                        uuid = api.add_dashboard(dashboard_data)
                        success_count += 1
                        UI.print_success(f"Added dashboard from {file_path} (UUID: {uuid})")
                    except Exception as e:
                        UI.print_error(f"Failed to add dashboard from {file_path}: {str(e)}")
                        failed_paths.append(file_path)
                        if not skip_errors:
                            raise
                    finally:
                        progress.update(task_id, advance=1)

            # Summary
            if success_count == total:
                UI.print_success(f"Successfully added all {total} dashboard{'s' if total > 1 else ''}")
            else:
                UI.print_warning(
                    f"Added {success_count} of {total} dashboard{'s' if total > 1 else ''}"
                    f"{'. Failed: ' + ', '.join(failed_paths) if failed_paths else ''}"
                )
        except Exception as e:
            UI.print_error(str(e))
            sys.exit(1) 
import json
import sys
from typing import Optional, List, Dict
import requests
from urllib.parse import urlparse
import re

from ..api.client import SignozAPI
from ..config.auth import TokenManager
from ..config.settings import CONFIG_FILE
from .ui import UI

SIGNOZ_DASHBOARDS_API = "https://api.github.com/repos/SigNoz/dashboards/git/trees/main?recursive=1"

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
    def delete_dashboards(api: SignozAPI, identifiers: List[str], force: bool = False, by_title: bool = False, remove_all: bool = False) -> None:
        """Handle delete command for multiple dashboards"""
        try:
            # First, get all dashboards
            all_dashboards = api.list_dashboards()
            
            # Collect UUIDs to delete
            uuids_to_delete = []
            
            if remove_all:
                # Get all dashboard UUIDs
                uuids_to_delete = [d['uuid'] for d in all_dashboards]
            elif by_title:
                for pattern in identifiers:
                    try:
                        # Convert glob-style pattern to regex pattern
                        regex_pattern = pattern.replace('*', '.*')
                        regex = re.compile(regex_pattern, re.IGNORECASE)
                        matches = [
                            dashboard['uuid'] for dashboard in all_dashboards
                            if regex.search(dashboard.get('data', {}).get('title', ''))
                        ]
                        if matches:
                            uuids_to_delete.extend(matches)
                        else:
                            UI.print_warning(f"No dashboards found matching pattern: {pattern}")
                    except re.error as e:
                        UI.print_error(f"Invalid pattern '{pattern}': {str(e)}")
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
            if (by_title or remove_all) and not force:
                UI.print_info("Dashboards to delete:")
                matched_dashboards = [
                    dashboard for dashboard in all_dashboards
                    if dashboard['uuid'] in unique_uuids
                ]
                for dashboard in matched_dashboards:
                    UI.print_info(f"  - {dashboard.get('data', {}).get('title', 'Untitled')} ({dashboard['uuid']})")
            
            # Extra confirmation for removing all dashboards
            if remove_all and not force:
                UI.print_warning(f"\nYou are about to remove ALL {total} dashboards!")
                UI.print_warning("This action cannot be undone.")
                if not UI.confirm_action("Are you absolutely sure?"):
                    UI.print_info("Operation cancelled")
                    return
            # Single confirmation if not force mode
            elif not force:
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
    def _fetch_available_dashboards() -> List[Dict]:
        """Fetch all available dashboards from SigNoz/dashboards repository"""
        try:
            response = requests.get(SIGNOZ_DASHBOARDS_API, timeout=10)  # Add timeout
            response.raise_for_status()
            data = response.json()
            
            # Filter only JSON files and organize by category
            dashboards = []
            for item in data.get('tree', []):
                if item['path'].endswith('.json'):
                    # Extract category from path
                    path_parts = item['path'].split('/')
                    category = path_parts[0] if len(path_parts) > 1 else 'Other'
                    dashboards.append({
                        'path': item['path'],
                        'category': category,
                        'url': f"https://raw.githubusercontent.com/SigNoz/dashboards/main/{item['path']}"
                    })
            
            # Sort by category and path
            dashboards.sort(key=lambda x: (x['category'], x['path']))
            return dashboards
        except requests.exceptions.Timeout:
            UI.print_error("Timeout while fetching dashboards. Please check your internet connection.")
            return []
        except requests.exceptions.RequestException as e:
            UI.print_error(f"Failed to fetch available dashboards: {str(e)}")
            return []
        except Exception as e:
            UI.print_error(f"Unexpected error while fetching dashboards: {str(e)}")
            return []

    @staticmethod
    def _parse_selection(selection: str, max_items: int) -> List[int]:
        """Parse selection string into list of indices"""
        indices = set()  # Use set to avoid duplicates
        
        # Split by comma first
        for part in selection.split(','):
            try:
                if '-' in part:
                    # Handle range (e.g., "5-10")
                    start, end = map(int, part.strip().split('-'))
                    if start < 1 or end > max_items or start > end:
                        UI.print_error(f"Invalid range: {start}-{end}. Please use numbers between 1 and {max_items}")
                        return []
                    indices.update(range(start-1, end))
                else:
                    # Handle single number
                    index = int(part.strip())
                    if 0 < index <= max_items:
                        indices.add(index-1)
                    else:
                        UI.print_error(f"Invalid selection: {index}. Please use numbers between 1 and {max_items}")
                        return []
            except ValueError:
                UI.print_error(f"Invalid input: '{part}'. Please use numbers only")
                return []
        
        return sorted(list(indices))

    @staticmethod
    def _select_dashboards(dashboards: List[Dict], pattern: Optional[str] = None) -> List[Dict]:
        """Allow user to select dashboards interactively"""
        if not dashboards:
            return []

        # If pattern is provided, filter dashboards
        if pattern:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                filtered = [d for d in dashboards if regex.search(d['path'])]
                if not filtered:
                    UI.print_warning(f"No dashboards found matching pattern: {pattern}")
                    return []
                return filtered
            except re.error as e:
                UI.print_error(f"Invalid regex pattern '{pattern}': {str(e)}")
                return []

        # Display available dashboards
        UI.display_available_dashboards(dashboards)
        
        # Get user selection
        selection = UI.prompt_dashboard_selection()
        if not selection:
            return []

        try:
            indices = Commands._parse_selection(selection, len(dashboards))
            if not indices:
                return []
            
            selected = [dashboards[i] for i in indices]
            
            # Show selected dashboards before proceeding
            if selected:
                UI.print_info("\nSelected dashboards:")
                for dash in selected:
                    UI.print_info(f"  - {dash['path']}")
            return selected
        except Exception as e:
            UI.print_error(f"Error processing selection: {str(e)}")
            return []

    @staticmethod
    def add_dashboards(api: SignozAPI, file_paths: List[str], skip_errors: bool = False, force: bool = False) -> None:
        """Handle add command for multiple dashboards"""
        try:
            # If no file paths provided, show available dashboards
            if not file_paths:
                dashboards = Commands._fetch_available_dashboards()
                if not dashboards:
                    UI.print_error("No dashboards available")
                    return
                
                selected = Commands._select_dashboards(dashboards)
                if not selected:
                    UI.print_info("No dashboards selected")
                    return
                
                file_paths = [d['url'] for d in selected]
            
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
                        title = dashboard_data.get('data', {}).get('title', 'Untitled')
                        UI.print_success(f"Added dashboard: {title} (UUID: {uuid})")
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
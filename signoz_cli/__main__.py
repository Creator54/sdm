#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from .api.client import SignozAPI
from .cli.commands import Commands
from .cli.ui import UI
from .config.settings import DEFAULT_API_URL

class CustomArgumentParser(argparse.ArgumentParser):
    def print_help(self):
        UI.print_help()

def main():
    # Load environment variables from .env file
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
    
    parser = CustomArgumentParser(description='SigNoz Dashboard CLI')
    parser.add_argument('--url', default=os.getenv('SIGNOZ_URL', DEFAULT_API_URL),
                      help=f'SigNoz API URL (default: from SIGNOZ_URL or {DEFAULT_API_URL})')
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login to get authentication token')
    login_parser.add_argument('--email', help='Email address (optional if set in .env)')
    login_parser.add_argument('--password', help='Password (optional if set in .env)')
    
    # Config command
    subparsers.add_parser('config', help='Show current configuration')
    
    # List command
    subparsers.add_parser('list', help='List all dashboards')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete one or more dashboards')
    delete_parser.add_argument('uuids', nargs='+', help='One or more dashboard UUIDs to delete')
    delete_parser.add_argument('--yes', '-y', action='store_true', help='Skip all confirmation prompts')
    delete_parser.add_argument('--force', '-f', action='store_true', help='Same as --yes, skip all confirmation prompts')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add one or more dashboards')
    add_parser.add_argument('files', nargs='+', help='One or more JSON files or URLs containing dashboard configurations')
    add_parser.add_argument('--skip-errors', '-s', action='store_true', help='Continue on error when adding multiple dashboards')
    add_parser.add_argument('--yes', '-y', action='store_true', help='Skip all confirmation prompts')
    
    # Add token argument to all commands except login and config
    for command in ['list', 'delete', 'add']:
        subparsers.choices[command].add_argument('--token', help='Authentication token (optional if logged in)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'login':
            api = SignozAPI(args.url)
            Commands.login(api, args.email, args.password)
        elif args.command == 'config':
            Commands.show_config()
        else:
            api = SignozAPI(args.url, args.token if hasattr(args, 'token') else None)
            
            if not api.token:
                UI.print_error("No token found. Please login first or provide a token.")
                sys.exit(1)
                
            if args.command == 'list':
                Commands.list_dashboards(api)
            elif args.command == 'delete':
                Commands.delete_dashboards(api, args.uuids, force=args.yes or args.force)
            elif args.command == 'add':
                Commands.add_dashboards(api, args.files, skip_errors=args.skip_errors, force=args.yes)
    except KeyboardInterrupt:
        UI.print_warning("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        UI.print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
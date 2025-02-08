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
    
    # Global options
    parser.add_argument('--url', '-u', default=os.getenv('SIGNOZ_URL', DEFAULT_API_URL),
                      help=f'SigNoz API URL (default: from SIGNOZ_URL or {DEFAULT_API_URL})')
    parser.add_argument('--token', '-t', help='Authentication token (optional if logged in)')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip all confirmation prompts')
    parser.add_argument('--force', '-f', action='store_true', help='Same as --yes')
    parser.add_argument('--skip-errors', '-s', action='store_true', help='Continue on error when adding multiple dashboards')
    parser.add_argument('--version', '-v', action='version', 
                      version=f'%(prog)s {__import__("signoz_cli").__version__}',
                      help='Show version')
    
    # Add login-specific options
    parser.add_argument('--email', '-e', help='Email address (optional if set in .env)')
    parser.add_argument('--password', '-p', help='Password (optional if set in .env)')
    parser.add_argument('--login', '-l', action='store_true', help='Login to SigNoz')
    
    # Command argument
    parser.add_argument('command', nargs='?', choices=['ls', 'rm', 'add', 'cfg'],
                      help='Command to execute (ls, rm, add, cfg)')
    
    # Arguments for commands
    parser.add_argument('args', nargs='*', help='Arguments for the command')
    
    args = parser.parse_args()
    
    try:
        # Handle login first as it's a special case
        if args.login:
            api = SignozAPI(args.url)
            Commands.login(api, args.email, args.password)
            return
            
        # Handle other commands
        if args.command == 'cfg':
            Commands.show_config()
            return
        elif args.command == 'ls':
            api = SignozAPI(args.url, args.token)
            if not api.token:
                UI.print_error("No token found. Please login first or provide a token.")
                sys.exit(1)
            Commands.list_dashboards(api)
            return
        elif args.command == 'rm':
            if not args.args:
                UI.print_error("Please provide at least one dashboard UUID to remove")
                sys.exit(1)
            api = SignozAPI(args.url, args.token)
            if not api.token:
                UI.print_error("No token found. Please login first or provide a token.")
                sys.exit(1)
            Commands.delete_dashboards(api, args.args, force=args.yes or args.force)
            return
        elif args.command == 'add':
            if not args.args:
                UI.print_error("Please provide at least one dashboard file to add")
                sys.exit(1)
            api = SignozAPI(args.url, args.token)
            if not api.token:
                UI.print_error("No token found. Please login first or provide a token.")
                sys.exit(1)
            Commands.add_dashboards(api, args.args, skip_errors=args.skip_errors, force=args.yes)
            return
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        UI.print_warning("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        UI.print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 
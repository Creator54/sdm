from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import print as rprint
from rich.style import Style

# Create console instance
console = Console()

# Styles
SUCCESS_STYLE = Style(color="green", bold=True)
ERROR_STYLE = Style(color="red", bold=True)
WARNING_STYLE = Style(color="yellow", bold=True)
INFO_STYLE = Style(color="blue", bold=True)
TITLE_STYLE = Style(color="cyan", bold=True)

class UI:
    @staticmethod
    def print_success(message: str) -> None:
        """Print success message"""
        console.print(f"✅ {message}", style=SUCCESS_STYLE)

    @staticmethod
    def print_error(message: str) -> None:
        """Print error message"""
        console.print(f"❌ {message}", style=ERROR_STYLE)

    @staticmethod
    def print_warning(message: str) -> None:
        """Print warning message"""
        console.print(f"⚠️ {message}", style=WARNING_STYLE)

    @staticmethod
    def print_info(message: str) -> None:
        """Print info message"""
        console.print(f"ℹ️ {message}", style=INFO_STYLE)

    @staticmethod
    def display_dashboards(dashboards: List[Dict[str, Any]]) -> None:
        """Display dashboards in a rich table"""
        if not dashboards:
            UI.print_info("No dashboards found")
            return

        table = Table(title="Available Dashboards", show_header=True, header_style=TITLE_STYLE)
        table.add_column("UUID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Created By", style="blue")

        for dashboard in dashboards:
            uuid = dashboard.get('uuid', 'N/A')
            title = dashboard.get('data', {}).get('title', 'Untitled')
            created_by = dashboard.get('created_by', 'Unknown')
            table.add_row(uuid, title, created_by)

        console.print(table)

    @staticmethod
    def display_config(config: Dict[str, Any]) -> None:
        """Display configuration in a rich panel"""
        if not config:
            UI.print_warning("No configuration found. Please login first.")
            return

        config_table = Table(show_header=False, show_edge=False)
        config_table.add_column("Key", style="cyan")
        config_table.add_column("Value", style="green")

        config_table.add_row("Email", config.get('email', 'Not set'))
        config_table.add_row("Last Login", config.get('last_login', 'Never'))
        config_table.add_row("Token", f"{config.get('token', 'Not set')[:20]}... (truncated)")
        config_table.add_row("Config Location", str(config.get('config_location', 'Unknown')))

        panel = Panel(
            config_table,
            title="[bold cyan]Current Configuration",
            border_style="blue"
        )
        console.print(panel)

    @staticmethod
    def confirm_action(message: str) -> bool:
        """Ask for user confirmation"""
        return Confirm.ask(message)

    @staticmethod
    def progress_context(message: str):
        """Create a progress context for long-running operations"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )

    @staticmethod
    def prompt(message: str, password: bool = False) -> str:
        """Prompt user for input"""
        return Prompt.ask(message, password=password)

    @staticmethod
    def print_help() -> None:
        """Display help information in a styled panel"""
        help_table = Table(show_header=False, show_edge=False)
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="green")

        # Commands
        help_table.add_row("[bold]Commands:", "")
        help_table.add_row("ls", "List all dashboards")
        help_table.add_row("rm UUID|PATTERN", "Delete dashboards by UUID or title pattern")
        help_table.add_row("add FILE...", "Add one or more dashboards")
        help_table.add_row("cfg", "Show current configuration")
        
        # Options
        help_table.add_row("", "")
        help_table.add_row("[bold]Options:", "")
        help_table.add_row("-l, --login", "Login to SigNoz")
        help_table.add_row("-u, --url", "Custom SigNoz API URL")
        help_table.add_row("-t, --token", "Authentication token")
        help_table.add_row("-e, --email", "Email for login")
        help_table.add_row("-p, --password", "Password for login")
        help_table.add_row("-y, --yes", "Skip all confirmation prompts")
        help_table.add_row("-s, --skip-errors", "Continue on errors (add command)")
        help_table.add_row("-T, --title", "Use regex pattern matching on dashboard titles")
        help_table.add_row("-v, --version", "Show version")

        # Examples
        help_table.add_row("", "")
        help_table.add_row("[bold]Examples:", "")
        help_table.add_row("signoz -l -e user@email.com", "Login with email")
        help_table.add_row("signoz ls", "List all dashboards")
        help_table.add_row("signoz rm UUID1 UUID2 -y", "Delete multiple dashboards without confirmation")
        help_table.add_row("signoz rm -T 'CPU.*' -y", "Delete matching dashboards without confirmation")
        help_table.add_row("signoz add dashboard.json -y", "Add a dashboard without confirmation")
        help_table.add_row("signoz cfg", "Show configuration")

        panel = Panel(
            help_table,
            title="[bold cyan]SigNoz Dashboard CLI Help",
            border_style="blue"
        )
        console.print(panel) 
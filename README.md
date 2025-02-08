# SigNoz Dashboard CLI

A powerful command-line interface for managing SigNoz dashboards. This tool allows you to easily manage your SigNoz dashboards through the command line, supporting operations like listing, adding, and deleting dashboards.

## Features

- 🔐 Secure authentication with JWT tokens
- 📊 List all available dashboards
- ➕ Add dashboards from local JSON files or URLs (including GitHub)
- 🗑️ Delete single or multiple dashboards
- 🔄 Batch operations support
- ⚡ Progress tracking for long operations
- 🎨 Beautiful CLI interface with rich formatting
- 🐧 Unix-style command flags

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/signoz-cli.git
cd signoz-cli
```

2. Install the package:
```bash
pip install -e .
```

## Configuration

You can configure the CLI in two ways:

1. Using environment variables in a `.env` file:
```bash
SIGNOZ_EMAIL=your.email@example.com
SIGNOZ_PASSWORD=your_password
SIGNOZ_URL=http://localhost:3301
```

2. Using command-line arguments:
```bash
signoz -l -e your.email@example.com -p your_password
```

## Usage

### Commands

The CLI uses Unix-style commands for all operations:

| Command | Description | Example |
|---------|-------------|---------|
| `ls` | List all dashboards | `signoz ls` |
| `rm` | Remove one or more dashboards | `signoz rm UUID1 UUID2` |
| `add` | Add one or more dashboards | `signoz add dash1.json dash2.json` |
| `cfg` | Show current configuration | `signoz cfg` |

### Global Options

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-l` | `--login` | Login to SigNoz |
| `-u` | `--url` | Custom SigNoz API URL |
| `-t` | `--token` | Authentication token |
| `-e` | `--email` | Email for login |
| `-p` | `--password` | Password for login |
| `-y` | `--yes` | Skip confirmations |
| `-f` | `--force` | Same as --yes |
| `-s` | `--skip-errors` | Continue on errors (for add command) |
| `-v` | `--version` | Show version |

### Examples

1. Authentication:
```bash
# Login with email/password
signoz -l -e user@example.com -p password

# Login using .env file
signoz -l

# Use custom API URL
signoz -l -u http://custom.signoz.url:3301
```

2. Managing Dashboards:
```bash
# List all dashboards
signoz ls

# Remove dashboards
signoz rm UUID1 UUID2         # Remove multiple dashboards
signoz rm UUID1 -y            # Remove without confirmation
signoz rm UUID1 UUID2 -f      # Force remove

# Add dashboards
signoz add dashboard.json                     # Add single dashboard
signoz add dash1.json dash2.json             # Add multiple dashboards
signoz add dash1.json dash2.json -s          # Continue on errors
signoz add dashboard.json -y                  # Add without confirmation
signoz add https://github.com/.../dash.json  # Add from URL
```

3. Configuration:
```bash
# Show current config
signoz cfg

# Use with custom token
signoz ls -t your_token
```

### Common Workflows

1. First-time setup:
```bash
# Set up configuration
signoz -l -e your.email@example.com -p your_password

# Verify configuration
signoz cfg

# List dashboards
signoz ls
```

2. Batch operations:
```bash
# Add multiple dashboards with error skipping
signoz add dash1.json dash2.json dash3.json -s -y

# Remove multiple dashboards without confirmation
signoz rm UUID1 UUID2 UUID3 -f
```

## Error Handling

The CLI provides clear error messages for common scenarios:

- Authentication failures
- Invalid dashboard JSON
- Network connectivity issues
- API errors
- File not found errors

## Security

- Credentials are never stored in plain text
- JWT tokens are stored securely with appropriate file permissions
- HTTPS is used for all API communications
- Sensitive information is masked in logs and output

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 
# SigNoz Dashboard Manager (sdm)

A minimal CLI tool for managing SigNoz dashboards.

## Install

```bash
git clone https://github.com/creator54/sdm.git
cd sdm && pip install -e .
```

## Configure

Using `.env`:
```bash
SIGNOZ_EMAIL=your.email@example.com
SIGNOZ_PASSWORD=your_password
SIGNOZ_URL=http://localhost:3301
```

Or CLI:
```bash
sdm -l -e your.email@example.com -p your_password
```

## Usage

### Basic Commands
```bash
sdm ls                      # List dashboards
sdm cfg                     # Show config
sdm add dash.json           # Add dashboard
sdm rm UUID                 # Remove by UUID
sdm rm -T "CPU.*"           # Remove by title pattern
```

### Options
| Flag | Description |
|------|-------------|
| `-l` | Login to SigNoz |
| `-u` | Custom API URL |
| `-t` | Auth token |
| `-e` | Email for login |
| `-p` | Password |
| `-y` | Skip confirmations |
| `-s` | Continue on errors (add) |
| `-T` | Use regex pattern matching |
| `-v` | Show version |

### Advanced Examples
```bash
# Batch operations
sdm add dash1.json dash2.json -s -y    # Add multiple, skip errors
sdm rm UUID1 UUID2 -y                  # Remove multiple
sdm rm -T "Host.*|CPU.*" -y            # Remove by pattern

# Remote dashboards
sdm add https://github.com/.../dash.json

# Pattern matching
sdm rm -T ".*Performance.*"            # Remove matching dashboards
sdm rm -T "Test.*|Dev.*"               # Remove multiple patterns
```

## Features

- 🔐 JWT authentication
- 📊 Dashboard management
- 🔍 Regex pattern matching
- 🚀 Batch operations
- ⚡ Progress tracking
- 🎨 Rich CLI interface

## License

MIT 
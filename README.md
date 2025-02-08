# SigNoz Dashboard Manager (sdm)

A minimal CLI tool for managing SigNoz dashboards.

## Install

```bash
git clone https://github.com/creator54/sdm.git
cd sdm && pip install -e .
```

### Using Nix

If you have Nix with flakes enabled, you can run the tool directly:

```bash
nix run github:creator54/sdm

# Or from local checkout
nix run .#
```

To install into your environment:
```bash
nix profile install github:creator54/sdm

# Or from local checkout
nix profile install .#
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
# Using default URL (http://localhost:3301)
sdm -l -e your.email@example.com -p your_password

# Using custom URL
sdm -l -e your.email@example.com -p your_password -u http://your.signoz.url:3301
```

## Usage

### Basic Commands
```bash
sdm ls                      # List dashboards
sdm cfg                     # Show config
sdm add                     # Browse & select dashboards from SigNoz/dashboards
sdm add dash.json           # Add specific dashboard
sdm rm UUID                 # Remove by UUID
sdm rm -T "*Metrics*"       # Remove by title pattern (glob-style)
sdm rm -a                   # Remove all dashboards
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
| `-s` | Continue on errors (for add and remove commands) |
| `-T` | Use glob pattern matching on titles (e.g., "*Metrics*", "JVM*") |
| `-a` | Remove all dashboards |
| `-v` | Show version |

### Advanced Examples
```bash
# Batch operations
sdm add dash1.json dash2.json -s -y      # Add multiple, skip errors
sdm rm UUID1 UUID2 -y -s                 # Remove multiple, continue on errors
sdm rm -T "*Host*|*CPU*" -y -s           # Remove by pattern, continue on errors
sdm rm -a -y                             # Remove all without confirmation

# Add dashboards
sdm add                                  # Interactive dashboard selection
sdm add https://github.com/.../dash.json # Add dashboard from URL or local file

# Pattern matching
sdm rm -T "*Performance*"                # Remove matching dashboards
sdm rm -T "Test*|Dev*"                  # Remove multiple patterns
```

## License

MIT 

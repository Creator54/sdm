# SigNoz Dashboard CLI

A command-line interface for managing SigNoz dashboards.

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
signoz login --email "your.email@example.com" --password "your_password"
```

## Usage

### Login
```bash
# Using .env file
signoz login

# Using command line arguments
signoz login --email "your.email@example.com" --password "your_password"
```

### View Configuration
```bash
signoz config
```

### List Dashboards
```bash
signoz list
```

### Delete Dashboard
```bash
signoz delete DASHBOARD_UUID
```

### Add Dashboard
```bash
signoz add dashboard.json
```

## Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## License

MIT License 
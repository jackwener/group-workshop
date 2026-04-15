# Report Compliance Audit Backend

Flask REST API for report compliance audit system.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python wsgi.py
```

## API Endpoints

- `GET /api/v1/compliance/capabilities` - System capabilities
- `GET /api/v1/compliance/health` - Health check

## Port

Backend runs on port **5000**.

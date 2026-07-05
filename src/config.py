import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists (for local development)
load_dotenv()

REQUIRED_VARS = [
    "MONGODB_URI",
    "FINNHUB_API_KEY",
    "SEC_EDGAR_USER_AGENT"
]

def validate_config():
    """Validates that all required environment variables are present, failing fast if not."""
    missing = []
    for var in REQUIRED_VARS:
        val = os.environ.get(var)
        if not val or val.strip() == "":
            missing.append(var)
    if missing:
        print(f"CRITICAL CONFIG ERROR: Missing required environment variable(s): {', '.join(missing)}", file=sys.stderr)
        print("Please set them in your shell environment or a local .env file.", file=sys.stderr)
        sys.exit(1)

# Validate config on import to enforce fail-fast behavior across all entrypoints
validate_config()

MONGODB_URI = os.environ["MONGODB_URI"]
FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]
SEC_EDGAR_USER_AGENT = os.environ["SEC_EDGAR_USER_AGENT"]

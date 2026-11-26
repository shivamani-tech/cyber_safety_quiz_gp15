from pathlib import Path

APP_NAME = "Cyber Safety Quiz"
HOST = "127.0.0.1"
PORT = 8000
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RECORDS_FILE = DATA_DIR / "records.json"
EXPORT_DIR = BASE_DIR / "exports"
MAX_REQUEST_BYTES = 16_384
PAGE_SIZE = 10
PASS_PERCENT = 70

from automation.config import LOG_DIR

PROCESSED_FILE = LOG_DIR / "processed.txt"


def _ensure():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not PROCESSED_FILE.exists():
        PROCESSED_FILE.touch()


def load_processed():
    _ensure()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def is_processed(timestamp):
    return timestamp in load_processed()


def mark_processed(timestamp):
    _ensure()
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(timestamp + "\n")
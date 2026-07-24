from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

KNOWLEDGE_BASE = ROOT_DIR / "knowledge_base"

PROJECTS_DIR = KNOWLEDGE_BASE / "projects"

REGISTRY_FILE = KNOWLEDGE_BASE / "registry" / "projects.yaml"

LOG_DIR = KNOWLEDGE_BASE / "logs"

PROCESSED_FILE = LOG_DIR / "processed.txt"

GOOGLE_SHEET_NAME = "Knowledge Base Updates"
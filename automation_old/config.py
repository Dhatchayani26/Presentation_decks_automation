from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

PROJECTS_DIR = ROOT_DIR / "projects"

REGISTRY_FILE = ROOT_DIR / "registry" / "projects.yaml"

PROJECT_TEMPLATE = ROOT_DIR / "templates" / "project_template.md"

LOG_DIR = ROOT_DIR / "logs"

GOOGLE_SHEET_NAME = "Knowledge Base Updates"
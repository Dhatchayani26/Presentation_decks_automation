import yaml

from automation.config import REGISTRY_FILE


def load_registry():

    if not REGISTRY_FILE.exists():
        return {}

    with open(REGISTRY_FILE, "r") as f:
        return yaml.safe_load(f) or {}


def save_registry(data):

    with open(REGISTRY_FILE, "w") as f:
        yaml.dump(data, f, sort_keys=False)


def project_exists(project_name: str) -> bool:
    registry = load_registry()
    return project_name in registry.get("projects", {})


def get_project(project_name: str):
    registry = load_registry()
    return registry.get("projects", {}).get(project_name)


def register_project(project_name: str, folder: str):
    registry = load_registry()

    registry.setdefault("projects", {})

    registry["projects"][project_name] = {
        "folder": folder
    }

    save_registry(registry)
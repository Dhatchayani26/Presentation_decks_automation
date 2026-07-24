from pathlib import Path

from automation.markdown_writer import update_section
from automation.registry import get_project
from automation.models import ProjectUpdate


def update_project(update: ProjectUpdate):

    project = get_project(update.project_name)

    if project is None:
        raise ValueError("Project not found")

    project_file = Path(project["folder"]) / "project.md"

    update_section(project_file, "OBJECTIVE", update.objective)

    update_section(project_file, "FEATURES", update.features)

    update_section(project_file, "HIGHLIGHTS", update.highlights)

    update_section(project_file, "LATEST_UPDATES", update.latest_changes)

    update_section(project_file, "TECH_STACK", update.tech_stack_updates)

    print(f"Updated {update.project_name}")
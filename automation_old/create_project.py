from pathlib import Path
import shutil

from automation.config import TEMPLATE_FILE
from automation.markdown_writer import update_section
from automation.registry import register_project
from automation.models import ProjectUpdate


def create_project(update: ProjectUpdate):

    folder = Path("knowledge_base/projects") / update.project_name.lower()

    folder.mkdir(parents=True, exist_ok=True)

    project_file = folder / "project.md"

    shutil.copy(TEMPLATE_FILE, project_file)

    update_section(project_file, "OBJECTIVE", update.objective)

    update_section(project_file, "FEATURES", update.features)

    update_section(project_file, "HIGHLIGHTS", update.highlights)

    update_section(project_file, "LATEST_UPDATES", update.latest_changes)

    update_section(project_file, "TECH_STACK", update.tech_stack_updates)

    register_project(
        update.project_name,
        str(folder)
    )

    print(f"Created {update.project_name}")
import os
import subprocess
from pathlib import Path
from datetime import datetime

from openai import files
import yaml
import gspread
from google.oauth2.service_account import Credentials


# ============================================================
# CONFIG
# ============================================================

GOOGLE_SHEET_NAME = "Project Updates (Responses)"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

ROOT = Path(__file__).parent

KB = ROOT / "knowledge_base"

PROJECTS = KB / "projects"

REGISTRY = KB / "registry" / "projects.yaml"

LOGS = KB / "logs"

PROCESSED = LOGS / "processed.txt"


# ============================================================
# SETUP
# ============================================================

PROJECTS.mkdir(parents=True, exist_ok=True)

LOGS.mkdir(parents=True, exist_ok=True)

REGISTRY.parent.mkdir(parents=True, exist_ok=True)

if not REGISTRY.exists():

    with open(REGISTRY, "w") as f:

        yaml.safe_dump({"projects": {}}, f)

if not PROCESSED.exists():

    PROCESSED.touch()


# ============================================================
# GOOGLE SHEETS
# ============================================================

def fetch_updates():

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    rows = sheet.get_all_records()
    rows = sheet.get_all_records()

    updates = []

    for row in rows:

        updates.append({

            "timestamp": str(row.get("Timestamp", "")),

            "team_lead": row.get("Team Lead Name", ""),

            "project_name": row.get("Project name", "").strip(),

            "client_name": row.get("Client Name", ""),

            "new_project": str(
                row.get(
                    "Is this a new project or an existing project?",
                    ""
                )
            ).lower(),

            "project_type": row.get("Project Type", ""),

            "objective": row.get(
                "What is the primary objective of the project?",
                ""
            ),

            "business_problem": row.get(
                "What business problem or client requirement",
                ""
            ),

            "features": row.get(
                "Features of the project(New)",
                ""
            ),

            "highlights": row.get(
                "What are the key highlights of the project that",
                ""
            ),

            "latest_changes": row.get(
                "What has changed or been achieved since the",
                ""
            ),

            "future_changes": row.get(
                "What changes are needed",
                ""
            )

        })

    return updates


# ============================================================
# PROCESSED LOG
# ============================================================

def load_processed():

    with open(PROCESSED, "r") as f:

        return {
            line.strip()
            for line in f
            if line.strip()
        }


def is_processed(timestamp):

    return timestamp in load_processed()


def mark_processed(timestamp):

    with open(PROCESSED, "a") as f:

        f.write(timestamp + "\n")

# ============================================================
# REGISTRY
# ============================================================

def load_registry():

    with open(REGISTRY, "r", encoding="utf-8") as f:

        data = yaml.safe_load(f)

    if data is None:
        data = {"projects": {}}

    if "projects" not in data:
        data["projects"] = {}

    return data


def save_registry(data):

    with open(REGISTRY, "w", encoding="utf-8") as f:

        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True
        )


def register_project(project_name, file_path):

    registry = load_registry()

    registry["projects"][project_name.lower()] = {
        "name": project_name,
        "path": str(file_path),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_registry(registry)


# ============================================================
# MARKDOWN
# ============================================================

def create_markdown(project):

    return f"""# {project['project_name']}

## Client

{project['client_name']}

---

## Team Lead

{project['team_lead']}

---

## Project Type

{project['project_type']}

---

## Objective

{project['objective']}

---

## Business Problem

{project['business_problem']}

---

## Features

{project['features']}

---

## Highlights

{project['highlights']}

---

## Latest Changes

{project['latest_changes']}

---

## Future Changes

{project['future_changes']}
"""


# ============================================================
# CREATE PROJECT
# ============================================================

def create_project(project):

    filename = (
        project["project_name"]
        .replace("/", "-")
        .replace("\\", "-")
        .strip()
        + ".md"
    )

    filepath = PROJECTS / filename

    with open(filepath, "w", encoding="utf-8") as f:

        f.write(create_markdown(project))

    register_project(
        project["project_name"],
        filepath
    )

    print(f"Created: {project['project_name']}")


# ============================================================
# UPDATE PROJECT
# ============================================================

def update_project(project):

    registry = load_registry()

    info = registry["projects"].get(
        project["project_name"].lower()
    )

    if info is None:

        create_project(project)

        return

    filepath = Path(info["path"])

    with open(filepath, "a", encoding="utf-8") as f:

        f.write(f"""

------------------------------------------------------------

# Update

Date:
{project['timestamp']}

## Highlights

{project['highlights']}

## Latest Changes

{project['latest_changes']}

## Features

{project['features']}

## Future Changes

{project['future_changes']}

""")

    register_project(
        project["project_name"],
        filepath
    )

    print(f"Updated: {project['project_name']}")


# ============================================================
# GIT
# ============================================================

def push_to_github():

    try:

        subprocess.run(["git", "add", "."], check=True)

        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"]
        )

        if diff.returncode == 0:

            print("\nNo git changes detected.")

            return

        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Knowledge Base Sync {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ],
            check=True
        )

        subprocess.run(
            ["git", "push"],
            check=True
        )

        print("\nGitHub updated successfully.")

    except Exception as e:

        print("\nGit Push Failed")

        print(e)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("Knowledge Base Sync Started")
    print("=" * 60)

    updates = fetch_updates()

    print(f"\nFound {len(updates)} responses\n")

    created = 0
    updated = 0
    skipped = 0

    registry = load_registry()

    processed = load_processed()

    for project in updates:

        timestamp = project["timestamp"]

        if timestamp in processed:

            print(f"Skipping : {project['project_name']}")

            skipped += 1

            continue

        project_name = project["project_name"]

        if not project_name:

            print("Skipping empty project name")

            continue

        exists = (
            project_name.lower()
            in registry["projects"]
        )

        try:

            if exists:

                update_project(project)

                updated += 1

            else:

                create_project(project)

                created += 1

            mark_processed(timestamp)

            processed.add(timestamp)

        except Exception as e:

            print(f"\nError processing {project_name}")

            print(e)

    print("\n")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"Created : {created}")
    print(f"Updated : {updated}")
    print(f"Skipped : {skipped}")

    push_to_github()

    print("\nDone.")


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    main()
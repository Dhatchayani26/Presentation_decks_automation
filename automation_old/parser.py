from automation.models import ProjectUpdate


def parse_row(row: dict) -> ProjectUpdate:
    """
    Convert one Google Sheet row into a ProjectUpdate object.
    """

    return ProjectUpdate(
        timestamp=row["Timestamp"],
        team_lead=row["Team Lead Name"],
        project_name=row["Project name"],
        client_name=row["Client Name"],
        is_new_project=(
            row["Is this a new project or an existing project?"]
            == "New Project"
        ),
        project_type=row["Project Type"],
        objective=row["What is the primary objective of the project?"],
        business_problem=row[
            "What business problem or client requirement does the project address?"
        ],
        features=row["Features of the project(New)"],
        highlights=row[
            "What are the key highlights of the project that should be showcased?"
        ],
        latest_changes=row[
            "What has changed or been achieved since the last update?"
        ],
        tech_stack_updates=row[
            "What changes are new with respect to Tech Stack ?"
        ],
    )
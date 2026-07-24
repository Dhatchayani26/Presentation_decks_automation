import gspread
from google.oauth2.service_account import Credentials

from automation.config import GOOGLE_SHEET_NAME
from automation.models import ProjectUpdate

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def fetch_updates():

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES,
    )

    client = gspread.authorize(credentials)

    sheet = client.open(GOOGLE_SHEET_NAME).sheet1

    rows = sheet.get_all_records()

    updates = []

    for row in rows:

        updates.append(
            ProjectUpdate(
                timestamp=str(row.get("Timestamp", "")),
                team_lead=str(row.get("Team Lead", "")),
                project_name=str(row.get("Project Name", "")).strip(),
                client_name=str(row.get("Client Name", "")),
                is_new_project=str(row.get("Is this a new project?", "")).strip().lower() == "yes",
                project_type=str(row.get("Project Type", "")),
                objective=str(row.get("Objective", "")),
                business_problem=str(row.get("Business Problem", "")),
                features=str(row.get("Features", "")),
                highlights=str(row.get("Highlights", "")),
                latest_changes=str(row.get("Latest Changes", "")),
                tech_stack_updates=str(row.get("Tech Stack Updates", "")),
            )
        )

    return updates

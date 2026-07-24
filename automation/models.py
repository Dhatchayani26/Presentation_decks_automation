from dataclasses import dataclass


@dataclass
class ProjectUpdate:
    timestamp: str
    team_lead: str
    project_name: str
    client_name: str
    is_new_project: bool
    project_type: str
    objective: str
    business_problem: str
    features: str
    highlights: str
    latest_changes: str
    tech_stack_updates: str
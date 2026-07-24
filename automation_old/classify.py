from automation.models import ProjectUpdate


def is_new_project(update: ProjectUpdate):

    return update.is_new_project
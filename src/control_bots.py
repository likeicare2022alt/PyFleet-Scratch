import scratchattach as sa
from scratchattach.utils.exceptions import CommentPostFailure


def post(project, text: str):
    try:
        project.post_comment(text)
    except CommentPostFailure:
        print("FAILED TO POST")


def connect(username, password, project_id):
    session = sa.login(username, password)
    return session.connect_project(project_id)

from flask import Blueprint, request

from models import Project

bp = Blueprint('/', __name__, url_prefix='/')


# @bp.context_processor
# def utility_processor():
#     """https://roytuts.com/context-processors-in-flask-api/"""
#
#     def get_all_projects():
#         return Project.query.all()
#
#     return dict(projects=get_all_projects())


@bp.context_processor
def utility_processor():
    """https://roytuts.com/context-processors-in-flask-api/"""

    def get_project():
        project_id = request.cookies.get('project_id', 1)
        project = Project.query.get_or_404(project_id)
        return project

    return dict(project=get_project())


from . import views
from . import hu

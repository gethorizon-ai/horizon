from app.routes.users import register_routes as register_users_routes
from app.routes.tasks import register_routes as register_tasks_routes
from app.routes.projects import register_routes as register_projects_routes
from app.routes.enablers import register_routes as register_enablers_routes

# from app.routes.prompts import register_routes as register_prompts_routes


def register_all_routes(api):
    register_users_routes(api)
    register_tasks_routes(api)
    register_projects_routes(api)
    # register_prompts_routes(api)
    register_enablers_routes(api)

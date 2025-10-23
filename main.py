from fastapi import FastAPI
from settings import settings
from api import router as api_router
from fastapi.openapi.utils import get_openapi


app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.project.title,
        version=settings.project.release_version,
        description=settings.project.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Введите токен в формате: Bearer <токен>"
        }
    }
    openapi_excluded_paths = [
        "/api/v1/users/registration",
        "/api/v1/users/authorization/login"
    ]

    for path, path_item in openapi_schema["paths"].items():
        if path not in openapi_excluded_paths:
            for operation in path_item.values():
                operation["security"] = [{"BearerAuth": []}]
        else:
            for operation in path_item.values():
                operation.pop("security", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(api_router, prefix="/api")

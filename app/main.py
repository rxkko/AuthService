from fastapi import FastAPI
from auth_middleware import AuthMiddleware
from routes import auth as auth_routes

app = FastAPI()
app.add_middleware(AuthMiddleware)

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
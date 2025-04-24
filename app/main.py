from fastapi import FastAPI
from auth_middleware import AuthMiddleware
from routes import auth as auth_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])

origins = [
    "http://localhost:8000",  # основной сервис
]
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Список разрешённых источников
    allow_credentials=True,          # Разрешаем куки и авторизацию
    allow_methods=["*"],             # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],             # Разрешаем все заголовки
)

@app.get("/")
def root():
    return {"message": "Hello from auth service"}
from fastapi import FastAPI
from auth_middleware import AuthMiddleware
from routes import auth as auth_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])

origins = [
    "http://localhost:8000",
]
app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         
    allow_credentials=True,       
    allow_methods=["*"],          
    allow_headers=["*"],         
)

@app.get("/")
def root():
    return {"message": "Hello from auth service"}

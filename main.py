from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import check_cve_2017_9248, check_cve_2017_5487, user_management

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(check_cve_2017_9248.router)
app.include_router(check_cve_2017_5487.router)
app.include_router(user_management.router)

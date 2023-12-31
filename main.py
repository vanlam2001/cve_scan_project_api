from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import check_cve_2017_9248, check_cve_2017_5487, user_management, test_send_mail, check_cve_2020_0796, exploit_cve_2020_0796, check_cve_2022_21907


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://zone-vn.vercel.app",
        "http://192.168.35.106:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(check_cve_2017_9248.router)
app.include_router(check_cve_2017_5487.router)
app.include_router(user_management.router)
app.include_router(test_send_mail.router)
app.include_router(check_cve_2020_0796.router)
app.include_router(exploit_cve_2020_0796.router)
app.include_router(check_cve_2022_21907.router)
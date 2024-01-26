from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from algorithm import generate_roster

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://roster-generator-webapp-git-development-api-in-9113f2-sdrummolo.vercel.app",
    "https://roster-generator-webapp-git-dev-sdrummolo.vercel.app",
    "https://roster-generator-webapp-git-alpha-sdrummolo.vercel.app",  # alpha preview
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Data(BaseModel):
    employees: int
    days: int
    shifts: int
    soft_days_off: bool


@app.get("/api/hello")
async def root():
    return {"message": "Hello world!"}


@app.post("/api/make_roster")
async def test(data: Data):
    return generate_roster(data.employees, data.days, data.shifts, data.soft_days_off)

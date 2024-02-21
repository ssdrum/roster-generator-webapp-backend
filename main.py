from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing_extensions import Annotated

from roster_solver import RosterProblem

app = FastAPI()

# Allowed origins
origins = [
    "http://localhost:3000",
    "https://roster-generator-webapp-git-development-api-in-9113f2-sdrummolo.vercel.app",
    "https://roster-generator-webapp-git-dev-sdrummolo.vercel.app",
    "https://roster-generator-webapp-git-alpha-sdrummolo.vercel.app",  # alpha preview
    "https://roster-generator-webapp-mocha.vercel.app",  # pro main
    "https://roster-generator-webapp-git-dev-luigi-di-paolo-s-team.vercel.app",  # pro dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class InputData(BaseModel):
    """
    This class models the input data and performs some basic input validation
    """

    num_employees: Annotated[int, Path(ge=1, le=30)]
    num_days: Annotated[int, Path(ge=1, le=7)]
    num_shifts: Annotated[int, Path(ge=1, le=10)]
    num_days_off: Annotated[int, Path(ge=0, le=4)]
    soft_days_off: bool


@app.get("/api/wakeup")
async def root():
    """
    This endpoint is used to "wake up" the production server, which runs on
    render.com's free tier. One limitation of the free tier is that the server
    shuts down after some period of inactifity. Restarting takes about a minute.
    Calling this endpoint when users first arrive on the page reduces the
    initial waiting time
    """
    return {"message": "5 more minutes please..."}


@app.post("/api/make_roster")
async def test(input_data: InputData):
    """
    This is the main endpoint for generating rosters
    """
    problem = RosterProblem(
        input_data.num_employees,
        input_data.num_days,
        input_data.num_shifts,
        input_data.num_days_off,
        input_data.soft_days_off,
    )
    return problem.make_roster()

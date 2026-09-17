from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from datetime import date, datetime


class UserSignupBirthdateModel(BaseModel):
    birthdate: date

class UserModel(UserSignupBirthdateModel):
    username: str


app = FastAPI()

def make_error(message: str, response: Response, status_code: int = 400):
    raise HTTPException(status_code=status_code, detail=message)

@app.put("/hello/{username}", status_code=204)
async def create_user(username: str, data: UserSignupBirthdateModel, response: Response):

    try:
        user_data = UserModel(
            username=username,
            birthdate=data.birthdate
        )
    except ValueError:
        make_error("Invalid date", response)

    TODAY = datetime.now().date()
    if user_data.birthdate > TODAY:
        make_error("Cannot be born in the future!", response)
    if user_data.birthdate.year < 1900:
        make_error("Vampires are not allowed!", response, status_code=403)

    # TODO: insert into DB

    if username == "exists":
        response.status_code = 409
        return {"message": "User already exists!"}

    return "" # HTTP 204 No content

def birthday_days_left(date: datetime) -> int:
    TODAY = datetime.now().date()
    next_birthday = date.replace(year=TODAY.year)
    
    # Corner case: LEAP DAY
    if next_birthday.day == 29 and next_birthday.month == 2:
        next_birthday.day = 28

    if next_birthday < TODAY:
        next_birthday = next_birthday.replace(year=TODAY.year + 1)

    return (next_birthday - today).days

@app.get("/hello/{username}")
async def get_user(username: str, response: Response):
    # TODO: Get user from DB
    user_data = UserModel(username=username, birthdate=datetime.strptime("1995-11-13", "%Y-%m-%d"))

    messages = list()
    messages.append(f"Hello, {user_data.username}!")

    days_left = birthday_days_left(user_data.birthdate)
    if days_left == 0:
        messages.append("Happy birthday!")
    else:
        messages.append(f"Your birthday is in {days_left} day(s)")

    return {"message": messages.join(" ")}

@app.get("/healthz/startup")
async def readiness():
    # TODO: check database availability
    return "OK"
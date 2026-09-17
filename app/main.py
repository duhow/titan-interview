from fastapi import FastAPI, Response
from pydantic import BaseModel
from datetime import datetime


class UserSignupModel(BaseModel):
    dateOfBirth: datetime


app = FastAPI()

def make_error(message: str, response: Response, status_code: int = 400):
    response.status_code = status_code
    raise Exception(message)

@app.put("/hello/{username}", status_code=204)
async def create_user(username: str, data: UserSignupModel, response: Response):
    
    try:
        user_data = {
            "username": username,
            "dateOfBirth": datetime.strptime(data.dateOfBirth, "%Y-%m-%d"),
        }
        TODAY = datetime.now().date()
        if user_data.dateOfBirth > TODAY:
            make_error("Cannot be born in the future!", response)
            
    except ValueError:
        make_error("Invalid date", response)
    
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
    user_data = UserSignupModel(dateOfBirth=datetime.strptime("1995-11-13", "%Y-%m-%d"))
    
    messages = list()
    messages.append(f"Hello, {username}!")
    
    days_left = birthday_days_left(user_data.dateOfBirth)
    if days_left == 0:
        messages.append("Happy birthday!")
    else:
        messages.append(f"Your birthday is in {days_left} day(s)")
        
    return {"message": messages.join(" ")}

@app.get("/healthz/startup")
async def readiness():
    # TODO: check database availability
    return "OK"
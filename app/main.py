from fastapi import FastAPI, Depends, Response, HTTPException
from sqlmodel import Session
from sqlalchemy import text

from app.database import get_session
from app.models import User

from pydantic import BaseModel
from datetime import date, datetime

class UserSignupBirthdateModel(BaseModel):
    birthdate: date

app = FastAPI()

@app.put("/hello/{username}", status_code=204)
async def create_user(
    username: str,
    data: UserSignupBirthdateModel,
    session: Session = Depends(get_session),
):

    user = User(
        username=username,
        birthdate=data.birthdate
    )

    TODAY = datetime.now().date()
    if user.birthdate > TODAY:
        raise HTTPException(400, "Cannot be born in the future!")
    if user.birthdate.year < 1900:
        raise HTTPException(403, "Vampires are not allowed!")
    if session.get(User, username):
        raise HTTPException(409, "User already exists!")

    # insert into DB
    session.add(user)
    session.commit()

    return "" # HTTP 204 No content

def birthday_days_left(date: datetime) -> int:
    TODAY = datetime.now().date()
    next_birthday = date.replace(year=TODAY.year)
    
    # Corner case: LEAP DAY
    if next_birthday.day == 29 and next_birthday.month == 2:
        next_birthday.day = 28

    if next_birthday < TODAY:
        next_birthday = next_birthday.replace(year=TODAY.year + 1)

    return (next_birthday - TODAY).days

@app.get("/hello/{username}")
async def get_user(
    username: str,
    session: Session = Depends(get_session),
):
    user = session.get(User, username)
    
    if not user:
        raise HTTPException(404, "User not found")

    messages = list()
    messages.append(f"Hello, {user.username}!")

    days_left = birthday_days_left(user.birthdate)
    if days_left == 0:
        messages.append("Happy birthday!")
    else:
        messages.append(f"Your birthday is in {days_left} day(s)")

    return {"message": " ".join(messages)}

@app.get("/healthz/startup")
async def readiness(
    session: Session = Depends(get_session),
):
    try:
        session.exec(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )

    return "OK"
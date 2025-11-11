"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from typing import List

from sqlmodel import Session, select

from .models import Activity, Participant, SQLModel
from .db import init_db, get_engine


app = FastAPI(title="Mergington High School API", description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    # initialize DB and create tables
    init_db()

    # seed DB if empty
    engine = get_engine()
    with Session(engine) as session:
        count = session.exec(select(Activity)).all()
        if not count:
            # Minimal seed data
            seeds = [
                Activity(name="Chess Club", description="Learn strategies and compete in chess tournaments", schedule="Fridays, 3:30 PM - 5:00 PM", max_participants=12),
                Activity(name="Programming Class", description="Learn programming fundamentals and build software projects", schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM", max_participants=20),
                Activity(name="Gym Class", description="Physical education and sports activities", schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", max_participants=30),
            ]
            session.add_all(seeds)
            session.commit()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(session: Session = Depends(get_session)):
    activities = {}
    results = session.exec(select(Activity)).all()
    for act in results:
        participants = session.exec(select(Participant).where(Participant.activity_id == act.id)).all()
        activities[act.name] = {
            "description": act.description or "",
            "schedule": act.schedule or "",
            "max_participants": act.max_participants,
            "participants": [p.email for p in participants],
        }
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    act = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    participants = session.exec(select(Participant).where(Participant.activity_id == act.id)).all()
    if any(p.email == email for p in participants):
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(participants) >= act.max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")

    participant = Participant(email=email, activity_id=act.id)
    session.add(participant)
    session.commit()
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, session: Session = Depends(get_session)):
    act = session.exec(select(Activity).where(Activity.name == activity_name)).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")

    participant = session.exec(select(Participant).where(Participant.activity_id == act.id, Participant.email == email)).first()
    if not participant:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    session.delete(participant)
    session.commit()
    return {"message": f"Unregistered {email} from {activity_name}"}

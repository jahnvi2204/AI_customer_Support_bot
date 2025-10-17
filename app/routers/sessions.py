from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as OrmSession
from ..db import get_db
from .. import models, schemas


router = APIRouter()


@router.post("/", response_model=schemas.SessionRead)
def create_session(payload: schemas.SessionCreate, db: OrmSession = Depends(get_db)):
    existing = db.get(models.Session, payload.session_id)
    if existing:
        return existing
    new_session = models.Session(id=payload.session_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/{session_id}", response_model=schemas.SessionRead)
def get_session(session_id: str, db: OrmSession = Depends(get_db)):
    session = db.get(models.Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/messages", response_model=list[schemas.MessageRead])
def list_session_messages(session_id: str, db: OrmSession = Depends(get_db)):
    session = db.get(models.Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages



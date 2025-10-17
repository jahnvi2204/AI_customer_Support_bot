from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as OrmSession
from ..db import get_db
from .. import models, schemas
from ..services.llm import generate_reply, summarize_session


router = APIRouter()


@router.post("/", response_model=schemas.ChatResponse)
def post_message(payload: schemas.MessageCreate, db: OrmSession = Depends(get_db)):
    session = db.get(models.Session, payload.session_id)
    if not session:
        session = models.Session(id=payload.session_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    user_msg = models.Message(session_id=payload.session_id, role="user", content=payload.content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    reply_text, escalated, faq_match_id = generate_reply(db, payload.session_id, payload.content)

    assistant_msg = models.Message(session_id=payload.session_id, role="assistant", content=reply_text)
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return schemas.ChatResponse(session_id=payload.session_id, reply=reply_text, escalated=escalated, faq_match_id=faq_match_id)


@router.get("/summary/{session_id}", response_model=schemas.SummaryResponse)
def get_summary(session_id: str, db: OrmSession = Depends(get_db)):
    session = db.get(models.Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    summary = summarize_session(db, session_id)
    return schemas.SummaryResponse(session_id=session_id, summary=summary)



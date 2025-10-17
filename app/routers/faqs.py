from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as OrmSession
from ..db import get_db
from .. import models, schemas


router = APIRouter()


@router.get("/", response_model=list[schemas.FAQRead])
def list_faqs(db: OrmSession = Depends(get_db)):
    return db.query(models.FAQ).all()


@router.post("/", response_model=schemas.FAQRead)
def create_faq(payload: schemas.FAQCreate, db: OrmSession = Depends(get_db)):
    faq = models.FAQ(question=payload.question, answer=payload.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq



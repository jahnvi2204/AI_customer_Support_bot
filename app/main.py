from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .db import init_db, SessionLocal
from .routers import sessions, messages, faqs
from . import models


def create_app() -> FastAPI:
    app = FastAPI(title="AI Customer Support Bot", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
    app.include_router(messages.router, prefix="/messages", tags=["messages"])
    app.include_router(faqs.router, prefix="/faqs", tags=["faqs"])

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()
        _seed_faqs()

    @app.get("/")
    def root():
        return RedirectResponse(url="/app/")

    app.mount("/app", StaticFiles(directory="frontend", html=True), name="static")

    return app


app = create_app()


def _seed_faqs() -> None:
    db = SessionLocal()
    try:
        count = db.query(models.FAQ).count()
        if count == 0:
            samples = [
                ("What are your support hours?", "Our support team is available 24/7 via chat and email."),
                ("How can I reset my password?", "Click 'Forgot password' on the sign-in page and follow the instructions."),
                ("How do I track my order?", "Go to Orders > Select your order > 'Track package' for real-time updates."),
                ("What is the refund policy?", "You can request a refund within 30 days of purchase subject to our policy."),
            ]
            for q, a in samples:
                db.add(models.FAQ(question=q, answer=a))
            db.commit()
    finally:
        db.close()



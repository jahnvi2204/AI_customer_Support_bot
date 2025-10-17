import os
from typing import Tuple, Optional
from sqlalchemy.orm import Session as OrmSession
from .. import models


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-8)


def _embed(text: str) -> list[float]:
    # Placeholder: simple hashing-based embedding for demo; swap with real embeddings
    import hashlib
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # produce a deterministic pseudo-embedding
    return [b / 255.0 for b in h[:64]]


def _retrieve_best_faq(db: OrmSession, user_text: str) -> tuple[Optional[models.FAQ], float]:
    faqs = db.query(models.FAQ).all()
    if not faqs:
        return None, 0.0
    user_vec = _embed(user_text)
    best, best_score = None, -1.0
    for f in faqs:
        q_vec = _embed(f.question)
        score = _cosine_similarity(user_vec, q_vec)
        if score > best_score:
            best, best_score = f, score
    return best, float(best_score)


def _llm_generate(prompt: str) -> str:
    # Minimal local stub to avoid external dependency in demo; replace with OpenAI API if configured
    return prompt[:1200]


def generate_reply(db: OrmSession, session_id: str, user_text: str) -> Tuple[str, bool, Optional[int]]:
    best_faq, score = _retrieve_best_faq(db, user_text)
    if best_faq and score >= 0.75:
        reply = best_faq.answer
        return reply, False, best_faq.id

    # Build conversation context
    messages = (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    history = []
    for m in messages[-8:]:  # recent context
        history.append(f"{m.role}: {m.content}")
    context = "\n".join(history)

    prompt = (
        "You are a helpful support assistant. If confident, answer succinctly. "
        "If unsure or missing data, recommend escalation to a human agent and propose next steps.\n\n"
        f"Conversation so far:\n{context}\n\nUser: {user_text}\nAssistant:"
    )
    raw = _llm_generate(prompt)

    escalated = False
    lower = raw.lower()
    if any(t in lower for t in ["not sure", "cannot", "uncertain", "escalate", "contact support", "agent"]):
        escalated = True

    return raw, escalated, best_faq.id if best_faq else None


def summarize_session(db: OrmSession, session_id: str) -> str:
    messages = (
        db.query(models.Message)
        .filter(models.Message.session_id == session_id)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    if not messages:
        return "No messages in this session."
    transcript = "\n".join(f"{m.role}: {m.content}" for m in messages)
    prompt = (
        "Summarize the following customer support conversation in 3-5 bullet points, "
        "include customer issue, resolutions attempted, and next actions.\n\n" + transcript
    )
    return _llm_generate(prompt)



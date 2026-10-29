"""
FastAPI High-Performance Async AI Microservice (backend/fastapi_app.py)
Provides REST and WebSocket endpoints for low-latency sentiment classification,
crisis guardian safety protocols, context tagging, and Vedic cognitive reframing.
"""

import os
import sys
from datetime import datetime
from typing import Optional, List, Dict, Any

# Ensure current and root paths are on sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from textblob import TextBlob

# Import wellness ML & reframing engines
try:
    import wellness_ml
except ImportError:
    try:
        from backend import wellness_ml
    except ImportError:
        wellness_ml = None

try:
    from cognitive_reframer import generate_therapeutic_response, CONTEXT_REFRAMINGS
except ImportError:
    from backend.cognitive_reframer import generate_therapeutic_response, CONTEXT_REFRAMINGS

# Authentic Sanskrit Gita Dictionary
GITA_SHLOKS = {
    "positive": [("कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।", "You have a right to perform your duties, but never to the fruits of those actions. — BG 2.47")],
    "negative": [("श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्।", "It is better to fail in one's own duty than to succeed in another’s. — BG 3.35")],
    "neutral": [("योगस्थः कुरु कर्माणि सङ्गं त्यक्त्वा धनञ्जय।", "Perform your duty equipoised, abandoning all attachment to success or failure. — BG 2.48")],
    "anxious": [("मा ते संगोऽस्त्वकर्मणि।", "Do not be attached to inaction or overwhelmed by the future. — BG 2.47")],
    "peaceful": [("शान्तिमाप्नोति नैष्ठिकीम्।", "One attains supreme peace by surrendering anxiety. — BG 5.12")],
    "angry": [("क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः।", "From anger comes delusion, from delusion the loss of memory and reason. — BG 2.63")],
    "very_happy": [("आत्मौपम्येन सर्वत्र समं पश्यति योऽर्जुन।", "That yogi sees all beings with equal vision, rejoicing in the welfare of all. — BG 6.32")],
    "pessimistic": [("नात्मानमवसादयेत्।", "Do not allow yourself to sink into despair; elevate yourself by the mind. — BG 6.5")],
    "optimistic": [("मां अनन्याश्चिन्तयन्तो ये जनाः पर्युपासते।", "Those who fix their mind on truth—I carry what they lack and preserve what they have. — BG 9.22")],
    "overwhelmed": [("युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु।", "Balance in eating, recreation, and actions brings supreme peace. — BG 6.17")],
    "restless": [("असंशयं महाबाहो मनो दुर्निग्रहं चलम्।", "Undoubtedly, the mind is restless and hard to control, but by practice and dispassion it is mastered. — BG 6.35")],
    "very_sad": [("न जायते म्रियते वा कदाचित्।", "The soul is eternal; it neither dies nor is born. You transcend temporary storms. — BG 2.20")],
    "sad": [("नेहाभिक्रमनाशोऽस्ति प्रत्यवायो न विद्यते।", "Even a small effort on this righteous path protects one from great fear. — BG 2.40")],
    "discouraged": [("यथा दीपो निवातस्थो नेङ्गते सोपमा स्मृता।", "Just as a lamp in a windless place does not flicker, remain steady in the self. — BG 6.19")],
    "devastated": [("नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः।", "Weapons do not cut the soul, fire does not burn it. Your sacred core is unharmed. — BG 2.23")]
}

CRISIS_PATTERNS = [
    r"\b(kill\s+myself|end\s+my\s+life|suicide|commit\s+suicide|want\s+to\s+die)\b",
    r"\b(hang\s+myself|overdose|cut\s+my\s+wrists|better\s+off\s+dead)\b",
    r"\b(severe\s+chest\s+pain|cannot\s+breathe|heart\s+attack|unconscious)\b"
]


def detect_crisis(text: str) -> bool:
    import re
    text_lower = text.lower()
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def detect_context(text: str) -> str:
    if 'classify_context_enhanced' in globals():
        return classify_context_enhanced(text)
    return "General Wellbeing"


# --- Pydantic Request & Response Models ---
class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, json_schema_extra={"example": "I feel overwhelmed with upcoming final exams and feel like I will fail."})

class AnalyzeResponse(BaseModel):
    polarity: float
    subjectivity: float
    mood: str
    context: str
    is_crisis: bool
    shlok: str
    shlok_meaning: str
    reframing: str
    affirmation: str
    micro_action: str
    philosophical_lens: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, json_schema_extra={"example": "I had a fight with my closest friend and feel terrible."})
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    mood: str
    context: str
    polarity: float
    is_crisis: bool
    shlok: str
    shlok_meaning: str
    affirmation: str
    micro_action: str
    timestamp: str


# --- FastAPI Application Instance ---
app = FastAPI(
    title="BhagvadMood & Sarathi Cognitive Reframing AI Microservice",
    description="High-performance async REST and WebSocket API delivering clinical mood detection, crisis interception, and Vedic cognitive reframing.",
    version="2.1.0"
)

# Enable Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root():
    return {
        "service": "BhagvadMood Cognitive Reframing AI Microservice",
        "version": "2.1.0",
        "status": "operational",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "chat": "POST /api/v1/chat",
            "analyze": "POST /api/v1/analyze",
            "verses": "GET /api/v1/verses",
            "health": "GET /api/v1/health",
            "websocket": "WS /ws/chat"
        }
    }


@app.get("/api/v1/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ml_engine": "active" if wellness_ml is not None else "numpy_fallback",
        "framework": "FastAPI + Uvicorn"
    }


@app.post("/api/v1/analyze", response_model=AnalyzeResponse, tags=["Sentiment & Cognitive Reframing"])
async def analyze_sentiment(payload: AnalyzeRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    # 1. Check Crisis
    is_crisis = detect_crisis(text)

    # 2. TextBlob Polarity & Subjectivity
    blob = TextBlob(text)
    polarity = float(blob.sentiment.polarity)
    subjectivity = float(blob.sentiment.subjectivity)

    # 3. Detect Context Driver
    context = detect_context(text)

    # 4. Neural Mood Prediction
    mood = "neutral"
    if wellness_ml is not None:
        try:
            mood, _ = wellness_ml.predict_mood(text)
        except Exception:
            mood = "positive" if polarity > 0.1 else ("negative" if polarity < -0.1 else "neutral")
    else:
        mood = "positive" if polarity > 0.1 else ("negative" if polarity < -0.1 else "neutral")

    # 5. Fetch Shlok
    shlok_pair = GITA_SHLOKS.get(mood.lower(), GITA_SHLOKS["neutral"])[0]
    shlok = shlok_pair[0]
    shlok_meaning = shlok_pair[1]

    # 6. Generate Therapeutic Reframing
    therapeutic = generate_therapeutic_response(text, mood, context, polarity)

    return AnalyzeResponse(
        polarity=polarity,
        subjectivity=subjectivity,
        mood=mood,
        context=context,
        is_crisis=is_crisis,
        shlok=shlok,
        shlok_meaning=shlok_meaning,
        reframing=therapeutic["reframing"],
        affirmation=therapeutic["affirmation"],
        micro_action=therapeutic["micro_action"],
        philosophical_lens=therapeutic["philosophical_lens"]
    )


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Conversational AI Chatbot"])
async def chat_message(payload: ChatRequest):
    text = payload.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Crisis Safety Guardian
    is_crisis = detect_crisis(text)
    if is_crisis:
        crisis_reply = (
            "🚨 **Immediate Safety Intervention:**\n\n"
            "I hear that you are experiencing intense pain right now. Please know that your life is deeply precious, "
            "and you do not have to walk through this alone. Immediate, compassionate human help is available 24/7:\n\n"
            "• **Tele-MANAS (Govt. of India):** Dial `14416` or `1800-891-4416`\n"
            "• **Vandrevala Foundation Helpline:** `+91 9999 666 555`\n"
            "• **KIRAN Helpline:** `1800-599-0019`\n"
            "• **National Emergency Service:** `112`\n\n"
            "Please pause, take a slow breath, and reach out to one of these verified resources immediately."
        )
        return ChatResponse(
            reply=crisis_reply,
            mood="crisis",
            context="Emergency Intervention",
            polarity=-1.0,
            is_crisis=True,
            shlok="सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
            shlok_meaning="Abandon all fear and take refuge in truth; you shall be protected from sorrow. — BG 18.66",
            affirmation="I am safe in this moment. Help is here for me.",
            micro_action="Call Tele-MANAS at 14416 immediately.",
            timestamp=datetime.now().isoformat()
        )

    # 2. Extract Sentiment & Context
    blob = TextBlob(text)
    polarity = float(blob.sentiment.polarity)
    context = detect_context(text)

    # 3. Neural Mood
    mood = "neutral"
    if wellness_ml is not None:
        try:
            mood, _ = wellness_ml.predict_mood(text)
        except Exception:
            mood = "positive" if polarity > 0.1 else ("negative" if polarity < -0.1 else "neutral")
    else:
        mood = "positive" if polarity > 0.1 else ("negative" if polarity < -0.1 else "neutral")

    # 4. Gita Pairing
    shlok_pair = GITA_SHLOKS.get(mood.lower(), GITA_SHLOKS["neutral"])[0]
    shlok = shlok_pair[0]
    shlok_meaning = shlok_pair[1]

    # 5. Synthesize Therapeutic Response
    therapeutic = generate_therapeutic_response(text, mood, context, polarity)

    # Build response reply
    formatted_reply = (
        f"{therapeutic['full_reply']}\n\n"
        f"📜 **Bhagavad Gita Wisdom:**\n"
        f"*{shlok}*\n"
        f"\"{shlok_meaning}\""
    )

    return ChatResponse(
        reply=formatted_reply,
        mood=mood,
        context=context,
        polarity=polarity,
        is_crisis=False,
        shlok=shlok,
        shlok_meaning=shlok_meaning,
        affirmation=therapeutic["affirmation"],
        micro_action=therapeutic["micro_action"],
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/v1/verses", tags=["Bhagavad Gita Wisdom"])
async def get_gita_verses(category: Optional[str] = Query("all")):
    verse_library = [
        {
            "chapter": 2, "verse": 47, "theme": "Anxiety & Action",
            "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
            "meaning": "You have a right to perform your prescribed duty, but never to the fruits of action. Never let outcomes be your motive, nor be attached to inaction.",
            "guidance": "Focus deeply on what is within your control right now. Anxiety arises when you fixate on future consequences rather than current duty."
        },
        {
            "chapter": 2, "verse": 20, "theme": "Fear & Mortality",
            "sanskrit": "न जायते म्रियते वा कदाचित् नायं भूत्वा भविता वा न भूयः। अजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे॥",
            "meaning": "The soul is neither born nor does it ever die. Unborn, eternal, ever-existing, and primeval, it is not slain when the body is slain.",
            "guidance": "Your true core is indestructible and transcends temporary emotional storms. Rest in this timeless sanctuary."
        },
        {
            "chapter": 6, "verse": 5, "theme": "Self-Doubt & Despair",
            "sanskrit": "उद्धरेदात्मनाऽऽत्मानं नात्मानमवसादयेत्। आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः॥",
            "meaning": "Elevate yourself by your own mind; do not degrade yourself. For the mind alone is the friend of the self, and the mind alone is the enemy.",
            "guidance": "Treat yourself with the kindness you would extend to a dear friend. Your mind can become your greatest ally through mindful patience."
        },
        {
            "chapter": 2, "verse": 63, "theme": "Anger & Frustration",
            "sanskrit": "क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः। स्मृतिभ्रंशाद् बुद्धिनाशो बुद्धिनाशात्प्रणश्यति॥",
            "meaning": "From anger arises delusion; from delusion comes confusion of memory; from confusion of memory comes loss of intellect; and from loss of intellect, destruction ensues.",
            "guidance": "When anger rises, pause before reacting. Recognize that reactive anger clouds your wisdom. Take 5 grounding breaths."
        },
        {
            "chapter": 6, "verse": 17, "theme": "Burnout & Overwhelm",
            "sanskrit": "युक्ताहारविहारस्य युक्तचेष्टस्य कर्मसु। युक्तस्वप्नावबोधस्य योगो भवति दुःखहा॥",
            "meaning": "He who is regulated in eating, recreation, work, sleep, and wakefulness attains yoga that destroys all sorrow.",
            "guidance": "Balance is sacred. Give yourself permission to pause, sleep, and nourish your body when feeling overwhelmed."
        },
        {
            "chapter": 3, "verse": 17, "theme": "Contentment & Peace",
            "sanskrit": "यस्त्वात्मरतिरेव स्यादात्मतृप्तश्च मानवः। आत्मन्येव च सन्तुष्टस्तस्य कार्यं न विद्यते॥",
            "meaning": "One who rejoices solely in the self, is satisfied with the self, and is content within, for him there are no anxious obligations.",
            "guidance": "True fulfillment comes from within, not external validation. Breathe and rest in your inherent completeness."
        }
    ]
    if category and category.lower() != "all":
        verse_library = [v for v in verse_library if category.lower() in v["theme"].lower()]
    return {"verses": verse_library, "total": len(verse_library)}


# Real-time WebSocket endpoint for continuous live chatbot interaction
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await websocket.send_json({
            "sender": "Sarathi",
            "message": "Namaste! I am Sarathi, your mindful companion. What is present in your heart today?",
            "timestamp": datetime.now().isoformat()
        })
        while True:
            data = await websocket.receive_text()
            if not data.strip():
                continue

            # Process through the chat workflow
            is_crisis = detect_crisis(data)
            if is_crisis:
                await websocket.send_json({
                    "sender": "Sarathi",
                    "is_crisis": True,
                    "message": "🚨 You are not alone. Please dial Tele-MANAS at 14416 or 112 immediately for free, 24/7 confidential support.",
                    "timestamp": datetime.now().isoformat()
                })
                continue

            blob = TextBlob(data)
            context = detect_context(data)
            mood = "neutral"
            if wellness_ml is not None:
                try:
                    mood, _ = wellness_ml.predict_mood(data)
                except Exception:
                    mood = "positive" if blob.sentiment.polarity > 0.1 else "negative"

            therapeutic = generate_therapeutic_response(data, mood, context, float(blob.sentiment.polarity))
            shlok_pair = GITA_SHLOKS.get(mood.lower(), GITA_SHLOKS["neutral"])[0]

            await websocket.send_json({
                "sender": "Sarathi",
                "is_crisis": False,
                "mood": mood,
                "context": context,
                "message": therapeutic["full_reply"],
                "shlok": shlok_pair[0],
                "meaning": shlok_pair[1],
                "affirmation": therapeutic["affirmation"],
                "micro_action": therapeutic["micro_action"],
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    print("[FASTAPI] Launching BhagvadMood FastAPI AI Microservice on http://127.0.0.1:8000...")
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=True)

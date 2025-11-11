import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional, List
from datetime import datetime, timezone
from database import create_document, get_documents, db
from schemas import Subscriber, Signal

app = FastAPI(title="Gold Signals API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Gold Signals API running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Request models
class SubscribeRequest(BaseModel):
    email: EmailStr
    plan: Literal['monthly', 'yearly']

class SignalCreateRequest(BaseModel):
    action: Literal['BUY', 'SELL']
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: Optional[int] = None
    timeframe: Optional[str] = 'M15'
    snapshot_url: Optional[str] = None
    note: Optional[str] = None

@app.post("/api/subscribe")
def subscribe(req: SubscribeRequest):
    data = Subscriber(email=req.email, plan=req.plan, status='active', started_at=datetime.now(timezone.utc))
    try:
        sub_id = create_document('subscriber', data)
        return {"status": "ok", "id": sub_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals", response_model=List[Signal])
def list_signals(limit: int = 10):
    try:
        docs = get_documents('signal', {}, limit)
        # Transform ObjectId and timestamps for JSON safety
        result = []
        for d in docs:
            d.pop('_id', None)
            if isinstance(d.get('created_at'), datetime):
                d['created_at'] = d['created_at'].isoformat()
            if isinstance(d.get('updated_at'), datetime):
                d['updated_at'] = d['updated_at'].isoformat()
            result.append(Signal(**{k: v for k, v in d.items() if k in Signal.model_fields}))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/signals")
def create_signal(req: SignalCreateRequest):
    signal = Signal(
        action=req.action,
        entry=req.entry,
        stop_loss=req.stop_loss,
        take_profit=req.take_profit,
        confidence=req.confidence,
        timeframe=req.timeframe,
        snapshot_url=req.snapshot_url,
        note=req.note,
    )
    try:
        sig_id = create_document('signal', signal)
        return {"status": "ok", "id": sig_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

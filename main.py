import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document, get_documents
from schemas import Booking

app = FastAPI(title="Vadakkumpuram Sree Vishnumaya Devasthanam API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Vadakkumpuram API running"}

@app.get("/api/services")
def list_services():
    services = [
        {"id": "badha-dosha-pariharam", "title": "Badha Dosha Pariharam", "summary": "Remove obstacles and negative influences.", "price": "On Request"},
        {"id": "black-magic-removal", "title": "Black Magic Removal", "summary": "Protection from dark energies.", "price": "On Request"},
        {"id": "sathru-samhara-pooja", "title": "Sathru Samhara Pooja", "summary": "Victory over enemies and challenges.", "price": "On Request"},
        {"id": "vishnumaya-blessing", "title": "Vishnumaya Blessing", "summary": "Receive divine grace and guidance.", "price": "On Request"},
        {"id": "vishnumaya-saktheya-pooja", "title": "Vishnumaya Saktheya Pooja", "summary": "Invoke powerful protection and strength.", "price": "On Request"},
        {"id": "real-estate-pooja", "title": "Real Estate Pooja", "summary": "Auspicious blessings for property matters.", "price": "On Request"},
    ]
    return {"services": services}

@app.post("/api/book")
def create_booking(booking: Booking):
    try:
        booking_id = create_document("booking", booking)
        return {"status": "success", "id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings")
def list_bookings(limit: int = 20):
    try:
        docs = get_documents("booking", limit=limit)
        # Convert ObjectId to string if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"bookings": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

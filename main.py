from fastapi import FastAPI
from pymongo import MongoClient
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Phone Lookup API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    MONGO_URL = os.environ.get("MONGO_URL")
    client = MongoClient(MONGO_URL)
    db = client["phone_db"]
    collection = db["phones"]
    print("✅ MongoDB Connected!")
except Exception as e:
    print(f"❌ Error: {e}")

@app.get("/")
def home():
    try:
        count = collection.count_documents({})
        return {"status": "online", "total_records": count}
    except:
        return {"status": "error"}

@app.get("/lookup/{mobile}")
def lookup(mobile: str):
    try:
        result = collection.find_one({"mobile": mobile})
        if not result:
            return {"success": False, "message": "Not found"}
        result.pop("_id", None)
        return {"success": True, "data": result}
    except:
        return {"success": False}

@app.get("/search")
def search(name: str = None, city: str = None):
    try:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if city:
            query["bill_city"] = {"$regex": city, "$options": "i"}
        
        results = list(collection.find(query).limit(10))
        for r in results:
            r.pop("_id", None)
        return {"success": True, "found": len(results), "results": results}
    except:
        return {"success": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

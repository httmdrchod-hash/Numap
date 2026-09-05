from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import glob

app = FastAPI(title="Phone Lookup API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.DataFrame()
xlsx_files = glob.glob("*.xlsx")
print(f"Found XLSX files: {xlsx_files}")

if xlsx_files:
    dfs = []
    for file in sorted(xlsx_files):
        try:
            temp_df = pd.read_excel(file, sheet_name=0)
            print(f"✅ Loaded {file}: {len(temp_df)} rows")
            dfs.append(temp_df)
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
    
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        print(f"✅ Total: {len(df)} records")
else:
    print("⚠️ No XLSX files found!")

df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

@app.get("/")
def home():
    return {"status": "online", "total_records": len(df), "example": "/lookup/7399095411"}

@app.get("/lookup/{mobile}")
def lookup(mobile: str):
    mobile = str(mobile).strip()
    result = df[df["mobile"] == mobile]
    
    if result.empty:
        return {"success": False, "message": f"Not found", "data": None}
    
    row = result.iloc[0].fillna("")
    return {"success": True, "data": row.to_dict()}

@app.get("/search")
def search(mobile: str = None, name: str = None, city: str = None):
    results = df.copy()
    if mobile:
        results = results[results["mobile"] == str(mobile).strip()]
    if name:
        results = results[results["name"].str.contains(name, case=False, na=False)]
    if city:
        results = results[results["bill_city"].str.contains(city, case=False, na=False)]
    
    if results.empty:
        return {"success": False, "found": 0, "data": []}
    
    records = results.head(10).to_dict('records')
    return {"success": True, "found": len(results), "results": records}

@app.get("/stats")
def stats():
    return {"total": len(df), "cities": df["bill_city"].nunique() if "bill_city" in df.columns else 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

from fastapi import FastAPI, Query, HTTPException
from service import fetch_brand_insights, fetch_competitors
from db import init_db, save_brand_data, get_all_brands, get_brand_by_id

app = FastAPI(title="Shopify Insights API")

init_db()

@app.get("/fetch-insights")
async def fetch_insights(website_url: str = Query(...)):
    data = fetch_brand_insights(website_url)
    if not data:
        raise HTTPException(status_code=404, detail="Could not fetch insights")
    save_brand_data(data["brand_name"], data)
    return data

@app.get("/fetch-competitors")
async def competitors(website_url: str = Query(...)):
    data = fetch_competitors(website_url)
    if not data:
        raise HTTPException(status_code=404, detail="No competitor data")
    return data

@app.get("/brands")
async def list_brands():
    return get_all_brands()

@app.get("/brand/{brand_id}")
async def brand_detail(brand_id: int):
    data = get_brand_by_id(brand_id)
    if not data:
        raise HTTPException(status_code=404, detail="Brand not found")
    return data

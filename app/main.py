from fastapi import FastAPI
from app.catalog import router as catalog_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="catalog-service")
app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"service": "catalog-service"}

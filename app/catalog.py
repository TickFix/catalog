from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.dynamo import get_dynamo
import os

router = APIRouter()
TABLE_NAME = os.getenv("CATALOG_TABLE", "catalog")

class CategoryIn(BaseModel):
    name: str
    subcategories: list[str]

@router.get("/categories")
async def list_categories():
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    resp = table.scan()
    return resp.get("Items", [])

@router.post("/categories")
async def create_category(data: CategoryIn):
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    item = {"pk": data.name.lower(), "name": data.name, "subcategories": data.subcategories}
    table.put_item(Item=item)
    return item

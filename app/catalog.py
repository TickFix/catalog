from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.dynamo import get_dynamo
import os

router = APIRouter()
TABLE_NAME = os.getenv("CATALOG_TABLE", "catalog")

class CategoryIn(BaseModel):
    name: str
    subcategories: list[str]

# ✅ ENDPOINTS EXISTENTES
@router.get("/categories")
async def list_categories():
    """Lista todas las categorías"""
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    resp = table.scan()
    return resp.get("Items", [])

@router.post("/categories")
async def create_category(data: CategoryIn):
    """Crea una nueva categoría"""
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    item = {"pk": data.name.lower(), "name": data.name, "subcategories": data.subcategories}
    table.put_item(Item=item)
    return item

# 🆕 NUEVO: Actualizar categoría (DynamoDB optimizado)
@router.put("/categories/{category_pk}")
async def update_category(category_pk: str, data: CategoryIn):
    """
    Actualiza una categoría existente en DynamoDB
    Usa update_item para eficiencia
    """
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    
    # Verificar si existe
    try:
        response = table.get_item(Key={"pk": category_pk})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Category not found")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Actualizar usando update_item (más eficiente en DynamoDB)
    try:
        response = table.update_item(
            Key={"pk": category_pk},
            UpdateExpression="SET #name = :name, subcategories = :subs",
            ExpressionAttributeNames={
                "#name": "name"  # 'name' es palabra reservada en DynamoDB
            },
            ExpressionAttributeValues={
                ":name": data.name,
                ":subs": data.subcategories
            },
            ReturnValues="ALL_NEW"
        )
        return response["Attributes"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")

# 🆕 NUEVO: Eliminar categoría
@router.delete("/categories/{category_pk}")
async def delete_category(category_pk: str):
    """
    Elimina una categoría de DynamoDB
    """
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    
    # Verificar si existe
    try:
        response = table.get_item(Key={"pk": category_pk})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Category not found")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Eliminar
    try:
        table.delete_item(Key={"pk": category_pk})
        return {"msg": "Category deleted successfully", "pk": category_pk}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting category: {str(e)}")

# 🆕 OPCIONAL: Obtener una categoría específica
@router.get("/categories/{category_pk}")
async def get_category(category_pk: str):
    """
    Obtiene una categoría específica por su pk
    """
    dynamo = get_dynamo()
    table = dynamo.Table(TABLE_NAME)
    
    try:
        response = table.get_item(Key={"pk": category_pk})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Category not found")
        return response["Item"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
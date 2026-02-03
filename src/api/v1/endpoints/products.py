from fastapi import APIRouter, HTTPException
from config.products import get_product_by_name, get_product_names

router = APIRouter()


@router.get("/")
async def list_products():
    return {"products": get_product_names()}


@router.get("/{product_name}")
async def get_product_detail(product_name: str):
    product = get_product_by_name(product_name)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product '{product_name}' not found"
        )
    if hasattr(product, "model_dump"):
        return product.model_dump()
    return product.__dict__

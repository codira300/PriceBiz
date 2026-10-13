from fastapi import APIRouter, Query

from app.controllers import search as search_controller


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("/products")
async def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    return await search_controller.search_products(
        search_term=q,
        limit=limit,
    )
from app.services.search import search_products as search_products_service


async def search_products(
    *,
    search_term: str,
    limit: int = 20,
):
    return await search_products_service(
        search_term,
        limit=limit,
    )
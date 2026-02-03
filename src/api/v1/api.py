from fastapi import APIRouter

from api.v1.endpoints import admin, auth, content, insights, misc, pipeline, products, webhooks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(
    content.router, tags=["content"]
)  # /hooks, /thumbnail, /video
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
api_router.include_router(webhooks.router, tags=["webhooks"])  # /webhooks/scheduler
api_router.include_router(misc.router, tags=["misc"])
api_router.include_router(insights.router, tags=["insights"])

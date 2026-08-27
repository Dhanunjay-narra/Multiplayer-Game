"""Unified API Gateway platform service for Nexus Frontier."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from server.database import init_db
from server.auth.routes import router as auth_router
from server.player.routes import router as player_router
from server.lobby.routes import router as lobby_router
from server.matchmaking.routes import router as matchmaking_router
from server.inventory.routes import router as inventory_router
from server.economy.routes import router as economy_router
from server.progression.routes import router as progression_router
from server.mission.routes import router as mission_router
from server.social.routes import router as social_router
from server.moderation.routes import router as moderation_router
from server.admin.routes import router as admin_router
from server.analytics.routes import router as analytics_router
from server.gateway.middleware import RateLimitMiddleware
from shared.logging.logger import setup_logger

logger = setup_logger("nexus.gateway")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database tables and background services on startup."""
    logger.info("Initializing Nexus Frontier Platform Services & Database...")
    await init_db()
    logger.info("Nexus Frontier Platform Services initialized successfully.")
    yield
    logger.info("Nexus Frontier Platform Services shutting down.")


app = FastAPI(
    title="Nexus Frontier - Platform API Gateway",
    description="Microservices API Gateway & real-time communication platform for Nexus Frontier.",
    version="0.1.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests_per_minute=200)

# Mount Routers
app.include_router(auth_router)
app.include_router(player_router)
app.include_router(lobby_router)
app.include_router(matchmaking_router)
app.include_router(inventory_router)
app.include_router(economy_router)
app.include_router(progression_router)
app.include_router(mission_router)
app.include_router(social_router)
app.include_router(moderation_router)
app.include_router(admin_router)
app.include_router(analytics_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Kubernetes liveness & readiness probes."""
    return {"status": "healthy", "service": "nexus-frontier-gateway", "version": "0.1.0"}


@app.websocket("/ws/gateway")
async def websocket_gateway_endpoint(websocket: WebSocket):
    """Real-time platform WebSocket connection for notifications and presence."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or process message
            await websocket.send_text(f'{{"type":"ack","received":{data}}}')
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

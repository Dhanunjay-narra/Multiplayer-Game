"""FastAPI endpoints for economy, wallets, trading, and marketplace."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user
from server.economy.wallet_service import wallet_service
from server.economy.trading_service import marketplace_service, trading_service
from shared.models.db_models import User
from shared.schemas.economy_schemas import WalletState, ShopListing

router = APIRouter(prefix="/api/v1/economy", tags=["Economy & Store"])


@router.get("/wallet", response_model=WalletState)
async def get_wallet(current_user: User = Depends(get_current_user)):
    """Returns all currency balances for the player."""
    return wallet_service.get_or_create_wallet(current_user.id)


@router.get("/store", response_model=List[ShopListing])
async def get_store_listings():
    """Returns active marketplace items with real-time dynamic pricing."""
    return list(marketplace_service.listings.values())


@router.post("/store/buy/{listing_id}")
async def buy_item(listing_id: str, quantity: int = 1, current_user: User = Depends(get_current_user)):
    """Purchases an item from the marketplace."""
    success = marketplace_service.buy_item(current_user.id, listing_id, quantity)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Purchase failed: Insufficient funds or stock")
    return {"message": "Purchase successful"}

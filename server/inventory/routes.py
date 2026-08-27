"""FastAPI endpoints for inventory and crafting."""
from fastapi import APIRouter, Depends, HTTPException, status
from server.auth.dependencies import get_current_user
from server.inventory.inventory_service import inventory_service
from server.inventory.crafting_service import crafting_service
from shared.models.db_models import User
from shared.schemas.inventory_schemas import InventoryGrid, ItemTransferRequest, CraftRequest, InventoryItemData

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory & Crafting"])


@router.get("", response_model=InventoryGrid)
async def get_inventory(current_user: User = Depends(get_current_user)):
    """Fetches the player's current inventory grid."""
    return inventory_service.get_or_create_inventory(current_user.id)


@router.post("/transfer")
async def transfer_item(req: ItemTransferRequest, current_user: User = Depends(get_current_user)):
    """Transfers or splits an item across inventory slots."""
    success = inventory_service.transfer_item(current_user.id, req)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid transfer request")
    return {"message": "Item transferred"}


@router.post("/craft", response_model=InventoryItemData)
async def craft_item(req: CraftRequest, current_user: User = Depends(get_current_user)):
    """Crafts an item using raw materials in inventory."""
    crafted = crafting_service.craft_item(current_user.id, req.recipe_id)
    if not crafted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient ingredients or invalid recipe")
    return crafted

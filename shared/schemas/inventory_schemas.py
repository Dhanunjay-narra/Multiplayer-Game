"""Inventory, item stack, transfer, and crafting schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import ItemCategory, ItemRarity


class InventoryItemData(BaseModel):
    item_id: str
    template_id: str
    name: str
    category: ItemCategory
    rarity: ItemRarity = ItemRarity.COMMON
    quantity: int = 1
    max_stack: int = 99
    durability: float = 100.0
    max_durability: float = 100.0
    is_locked: bool = False
    attributes: Dict[str, float] = Field(default_factory=dict)


class InventoryGrid(BaseModel):
    inventory_id: str
    owner_id: str
    max_slots: int = 24
    slots: Dict[int, Optional[InventoryItemData]] = Field(default_factory=dict)


class ItemTransferRequest(BaseModel):
    source_slot: int
    destination_slot: int
    quantity: int = 1


class CraftingIngredient(BaseModel):
    template_id: str
    quantity: int = 1


class CraftingRecipe(BaseModel):
    recipe_id: str
    output_template_id: str
    output_quantity: int = 1
    ingredients: List[CraftingIngredient]
    required_level: int = 1
    crafting_time_seconds: float = 2.0
    energy_cost: float = 50.0


class CraftRequest(BaseModel):
    recipe_id: str

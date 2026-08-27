"""Crafting recipes, material consumption, and blueprint processing."""
import uuid
from typing import Dict, List, Optional
from shared.schemas.inventory_schemas import CraftingRecipe, CraftingIngredient, InventoryItemData
from shared.enums.game_enums import ItemCategory, ItemRarity
from server.inventory.inventory_service import inventory_service


class CraftingService:
    """Manages data-driven recipes and creates weapons/modules from resources."""

    def __init__(self) -> None:
        self.recipes: Dict[str, CraftingRecipe] = {}
        self._init_default_recipes()

    def _init_default_recipes(self) -> None:
        # Recipe: Craft Plasma Sniper
        self.recipes["rcp_plasma_sniper"] = CraftingRecipe(
            recipe_id="rcp_plasma_sniper",
            output_template_id="wpn_sniper_apex",
            output_quantity=1,
            ingredients=[
                CraftingIngredient(template_id="mat_alloy_bar", quantity=20),
            ],
            required_level=2,
            crafting_time_seconds=3.0,
            energy_cost=100.0,
        )
        # Recipe: Craft Nanite Medkit
        self.recipes["rcp_nanite_medkit"] = CraftingRecipe(
            recipe_id="rcp_nanite_medkit",
            output_template_id="con_nanite_stim",
            output_quantity=3,
            ingredients=[
                CraftingIngredient(template_id="mat_alloy_bar", quantity=5),
            ],
            required_level=1,
            crafting_time_seconds=1.0,
            energy_cost=25.0,
        )

    def craft_item(self, user_id: str, recipe_id: str) -> Optional[InventoryItemData]:
        """Validates ingredients and produces crafted item in user inventory."""
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return None

        inv = inventory_service.get_or_create_inventory(user_id)

        # Check ingredients
        for ing in recipe.ingredients:
            available_qty = sum(
                item.quantity for item in inv.slots.values()
                if item and item.template_id == ing.template_id
            )
            if available_qty < ing.quantity:
                return None

        # Consume ingredients
        for ing in recipe.ingredients:
            needed = ing.quantity
            for slot_idx, item in list(inv.slots.items()):
                if item and item.template_id == ing.template_id:
                    deduct = min(needed, item.quantity)
                    item.quantity -= deduct
                    needed -= deduct
                    if item.quantity <= 0:
                        inv.slots[slot_idx] = None
                    if needed <= 0:
                        break

        # Generate output item
        crafted_item = InventoryItemData(
            item_id=f"item_{uuid.uuid4().hex[:8]}",
            template_id=recipe.output_template_id,
            name="Apex Particle Lance" if "sniper" in recipe.output_template_id else "Nanite Stim",
            category=ItemCategory.WEAPON if "wpn" in recipe.output_template_id else ItemCategory.CONSUMABLE,
            rarity=ItemRarity.RARE if "sniper" in recipe.output_template_id else ItemRarity.COMMON,
            quantity=recipe.output_quantity,
        )
        inventory_service.add_item(user_id, crafted_item)
        return crafted_item


crafting_service = CraftingService()

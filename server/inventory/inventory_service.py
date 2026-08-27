"""Inventory slot management, item stacking, splitting, and durability."""
import uuid
from typing import Dict, List, Optional
from shared.schemas.inventory_schemas import InventoryGrid, InventoryItemData, ItemTransferRequest
from shared.enums.game_enums import ItemCategory, ItemRarity


class InventoryService:
    """Manages player item storage grids with slot constraints and stack limits."""

    def __init__(self) -> None:
        self._inventories: Dict[str, InventoryGrid] = {}

    def get_or_create_inventory(self, user_id: str, max_slots: int = 24) -> InventoryGrid:
        """Retrieves or creates player inventory."""
        if user_id not in self._inventories:
            grid = InventoryGrid(inventory_id=f"inv_{user_id}", owner_id=user_id, max_slots=max_slots)
            # Add initial starting gear
            grid.slots[0] = InventoryItemData(
                item_id=f"item_{uuid.uuid4().hex[:8]}",
                template_id="wpn_rifle_v44",
                name="V-44 Kinetic Liberator",
                category=ItemCategory.WEAPON,
                rarity=ItemRarity.COMMON,
                quantity=1,
                durability=100.0,
            )
            grid.slots[1] = InventoryItemData(
                item_id=f"item_{uuid.uuid4().hex[:8]}",
                template_id="mat_alloy_bar",
                name="Titanium-Alloy Ingot",
                category=ItemCategory.RESOURCE,
                rarity=ItemRarity.COMMON,
                quantity=25,
                max_stack=999,
            )
            self._inventories[user_id] = grid
        return self._inventories[user_id]

    def add_item(self, user_id: str, item: InventoryItemData) -> bool:
        """Adds an item to an existing stack or first available free slot."""
        inv = self.get_or_create_inventory(user_id)

        # 1. Try stacking
        for slot_idx, slot_item in inv.slots.items():
            if slot_item and slot_item.template_id == item.template_id and slot_item.quantity < slot_item.max_stack:
                space = slot_item.max_stack - slot_item.quantity
                added = min(space, item.quantity)
                slot_item.quantity += added
                item.quantity -= added
                if item.quantity <= 0:
                    return True

        # 2. Find empty slot
        for slot_idx in range(inv.max_slots):
            if slot_idx not in inv.slots or inv.slots[slot_idx] is None:
                inv.slots[slot_idx] = item
                return True

        return False  # Inventory full

    def transfer_item(self, user_id: str, req: ItemTransferRequest) -> bool:
        """Moves or splits item from source slot to destination slot."""
        inv = self.get_or_create_inventory(user_id)
        if req.source_slot not in inv.slots or inv.slots[req.source_slot] is None:
            return False

        src_item = inv.slots[req.source_slot]
        if req.destination_slot >= inv.max_slots or req.destination_slot < 0:
            return False

        dest_item = inv.slots.get(req.destination_slot)
        if dest_item is None:
            # Move entire item or split
            if req.quantity >= src_item.quantity:
                inv.slots[req.destination_slot] = src_item
                inv.slots[req.source_slot] = None
            else:
                src_item.quantity -= req.quantity
                new_item = src_item.model_copy()
                new_item.item_id = f"item_{uuid.uuid4().hex[:8]}"
                new_item.quantity = req.quantity
                inv.slots[req.destination_slot] = new_item
            return True
        elif dest_item.template_id == src_item.template_id:
            # Merge stacks
            space = dest_item.max_stack - dest_item.quantity
            move_qty = min(space, min(req.quantity, src_item.quantity))
            dest_item.quantity += move_qty
            src_item.quantity -= move_qty
            if src_item.quantity <= 0:
                inv.slots[req.source_slot] = None
            return True

        return False


inventory_service = InventoryService()

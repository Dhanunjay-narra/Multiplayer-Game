"""Unit tests for inventory stacking, crafting, wallets, and marketplace."""
import pytest
from server.inventory.inventory_service import InventoryService
from server.inventory.crafting_service import CraftingService
from server.economy.wallet_service import WalletService
from server.economy.trading_service import TradingService, MarketplaceService
from shared.enums.game_enums import CurrencyType, ItemCategory, ItemRarity
from shared.schemas.inventory_schemas import InventoryItemData, ItemTransferRequest


def test_inventory_stacking_and_transfer():
    inv_svc = InventoryService()
    user_id = "test_user_01"
    grid = inv_svc.get_or_create_inventory(user_id)
    assert len(grid.slots) >= 2

    # Transfer / split item
    req = ItemTransferRequest(source_slot=1, destination_slot=5, quantity=10)
    success = inv_svc.transfer_item(user_id, req)
    assert success is True
    assert grid.slots[5].quantity == 10
    assert grid.slots[1].quantity == 15


def test_crafting_execution():
    inv_svc = InventoryService()
    craft_svc = CraftingService()
    user_id = "test_user_craft"
    inv_svc.get_or_create_inventory(user_id)

    # Craft Plasma Sniper (requires 20 alloy bars, starting gear has 25)
    crafted = craft_svc.craft_item(user_id, "rcp_plasma_sniper")
    assert crafted is not None
    assert crafted.template_id == "wpn_sniper_apex"


def test_wallet_and_ledger():
    wal_svc = WalletService()
    user_id = "test_user_wal"
    wal = wal_svc.get_or_create_wallet(user_id)
    assert wal.balances[CurrencyType.CREDITS] == 1000.0

    # Modify balance
    success = wal_svc.modify_balance(user_id, CurrencyType.CREDITS, -250.0, "Test Purchase")
    assert success is True
    assert wal.balances[CurrencyType.CREDITS] == 750.0

    # Overdraft prevention
    fail_res = wal_svc.modify_balance(user_id, CurrencyType.CREDITS, -1000.0, "Illegal Overdraft")
    assert fail_res is False
    assert wal.balances[CurrencyType.CREDITS] == 750.0


def test_marketplace_demand_pricing():
    mkt_svc = MarketplaceService()
    wal_svc = WalletService()
    user_id = "test_buyer"
    wal_svc.get_or_create_wallet(user_id)

    initial_price = mkt_svc.listings["shop_stim"].current_price
    # Buy 2 items
    mkt_svc.buy_item(user_id, "shop_stim", quantity=2)
    new_price = mkt_svc.listings["shop_stim"].current_price
    assert new_price > initial_price  # Price increases with demand

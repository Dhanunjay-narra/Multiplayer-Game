"""Currencies, marketplace transactions, wallet state, and escrow trading schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from shared.enums.game_enums import CurrencyType
from shared.schemas.inventory_schemas import InventoryItemData


class WalletState(BaseModel):
    user_id: str
    balances: Dict[CurrencyType, float] = Field(default_factory=lambda: {
        CurrencyType.CREDITS: 1000.0,
        CurrencyType.ENERGY_CELLS: 100.0,
        CurrencyType.ALLOY_MATERIALS: 50.0,
        CurrencyType.FACTION_TOKENS: 0.0,
        CurrencyType.SEASON_TOKENS: 0.0,
    })


class TransactionEntry(BaseModel):
    transaction_id: str
    user_id: str
    currency: CurrencyType
    amount: float
    balance_after: float
    description: str
    timestamp: float


class ShopListing(BaseModel):
    listing_id: str
    item_template_id: str
    item_name: str
    base_price: float
    current_price: float
    currency: CurrencyType = CurrencyType.CREDITS
    stock: int = 100
    demand_factor: float = 1.0


class TradeOffer(BaseModel):
    trade_id: str
    initiator_id: str
    target_id: str
    initiator_items: List[InventoryItemData] = Field(default_factory=list)
    initiator_credits: float = 0.0
    target_items: List[InventoryItemData] = Field(default_factory=list)
    target_credits: float = 0.0
    initiator_locked: bool = False
    target_locked: bool = False
    is_confirmed: bool = False
    is_cancelled: bool = False

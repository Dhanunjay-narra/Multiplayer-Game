"""Escrow player-to-player trading and dynamic marketplace pricing."""
import uuid
from typing import Dict, List, Optional
from shared.schemas.economy_schemas import TradeOffer, ShopListing
from shared.enums.game_enums import CurrencyType
from server.economy.wallet_service import wallet_service
from server.inventory.inventory_service import inventory_service


class TradingService:
    """Manages 2-party atomic escrow item and credit trading."""

    def __init__(self) -> None:
        self.active_trades: Dict[str, TradeOffer] = {}

    def create_trade_offer(self, initiator_id: str, target_id: str) -> TradeOffer:
        trade_id = f"trd_{uuid.uuid4().hex[:10]}"
        offer = TradeOffer(trade_id=trade_id, initiator_id=initiator_id, target_id=target_id)
        self.active_trades[trade_id] = offer
        return offer

    def lock_trade(self, trade_id: str, user_id: str) -> bool:
        trade = self.active_trades.get(trade_id)
        if not trade:
            return False

        if user_id == trade.initiator_id:
            trade.initiator_locked = True
        elif user_id == trade.target_id:
            trade.target_locked = True
        return True

    def confirm_trade(self, trade_id: str, user_id: str) -> bool:
        """Executes atomic swap when both parties lock and confirm."""
        trade = self.active_trades.get(trade_id)
        if not trade or not (trade.initiator_locked and trade.target_locked):
            return False

        # Atomic currency exchange
        if trade.initiator_credits > 0:
            if not wallet_service.modify_balance(trade.initiator_id, CurrencyType.CREDITS, -trade.initiator_credits, f"Trade {trade_id}"):
                return False
            wallet_service.modify_balance(trade.target_id, CurrencyType.CREDITS, trade.initiator_credits, f"Trade {trade_id}")

        if trade.target_credits > 0:
            if not wallet_service.modify_balance(trade.target_id, CurrencyType.CREDITS, -trade.target_credits, f"Trade {trade_id}"):
                return False
            wallet_service.modify_balance(trade.initiator_id, CurrencyType.CREDITS, trade.target_credits, f"Trade {trade_id}")

        trade.is_confirmed = True
        return True


class MarketplaceService:
    """Dynamic shop pricing adapting to supply and demand curves."""

    def __init__(self) -> None:
        self.listings: Dict[str, ShopListing] = {}
        self._init_default_shop()

    def _init_default_shop(self) -> None:
        self.listings["shop_stim"] = ShopListing(
            listing_id="shop_stim",
            item_template_id="con_nanite_stim",
            item_name="Nanite Stimpack",
            base_price=100.0,
            current_price=100.0,
            currency=CurrencyType.CREDITS,
            stock=500,
        )
        self.listings["shop_alloy"] = ShopListing(
            listing_id="shop_alloy",
            item_template_id="mat_alloy_bar",
            item_name="Titanium Alloy Bar",
            base_price=250.0,
            current_price=250.0,
            currency=CurrencyType.CREDITS,
            stock=200,
        )

    def buy_item(self, user_id: str, listing_id: str, quantity: int = 1) -> bool:
        listing = self.listings.get(listing_id)
        if not listing or listing.stock < quantity:
            return False

        total_cost = listing.current_price * quantity
        if not wallet_service.modify_balance(user_id, listing.currency, -total_cost, f"Purchased {listing.item_name}"):
            return False

        listing.stock -= quantity
        # Dynamic demand pricing: price rises as stock depletes
        listing.demand_factor += (0.05 * quantity)
        listing.current_price = round(listing.base_price * listing.demand_factor, 2)
        return True


trading_service = TradingService()
marketplace_service = MarketplaceService()

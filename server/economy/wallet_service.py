"""Multi-currency wallet ledger and transactional accounting."""
import uuid
import time
from typing import Dict, List, Optional
from shared.enums.game_enums import CurrencyType
from shared.schemas.economy_schemas import WalletState, TransactionEntry


class WalletService:
    """Manages player wallets, balances, and audit transactions."""

    def __init__(self) -> None:
        self._wallets: Dict[str, WalletState] = {}
        self._ledger: List[TransactionEntry] = []

    def get_or_create_wallet(self, user_id: str) -> WalletState:
        if user_id not in self._wallets:
            self._wallets[user_id] = WalletState(user_id=user_id)
        return self._wallets[user_id]

    def modify_balance(
        self,
        user_id: str,
        currency: CurrencyType,
        amount: float,
        description: str,
    ) -> bool:
        """Atomically modifies a currency balance with ledger recording."""
        wallet = self.get_or_create_wallet(user_id)
        current_bal = wallet.balances.get(currency, 0.0)

        if current_bal + amount < 0:
            return False  # Insufficient funds

        new_bal = current_bal + amount
        wallet.balances[currency] = round(new_bal, 2)

        # Record ledger transaction
        tx = TransactionEntry(
            transaction_id=f"tx_{uuid.uuid4().hex[:10]}",
            user_id=user_id,
            currency=currency,
            amount=amount,
            balance_after=wallet.balances[currency],
            description=description,
            timestamp=time.time(),
        )
        self._ledger.append(tx)
        return True


wallet_service = WalletService()

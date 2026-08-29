from dataclasses import dataclass
from typing import Dict

@dataclass
class DynamicMarketEngine:
    base_prices: Dict[str, float]
    demand_multipliers: Dict[str, float]

    def calculate_price(self, item_id: str, quantity_demanded: int) -> float:
        base = self.base_prices.get(item_id, 100.0)
        multiplier = self.demand_multipliers.get(item_id, 1.0)
        surge = 1.0 + (quantity_demanded * 0.02)
        return round(base * multiplier * surge, 2)

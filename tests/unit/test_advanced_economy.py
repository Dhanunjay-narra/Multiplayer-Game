from server.economy.market_engine import DynamicMarketEngine

def test_dynamic_market_surge_pricing():
    engine = DynamicMarketEngine(
        base_prices={"plasma_rifle": 500.0, "nano_shield": 250.0},
        demand_multipliers={"plasma_rifle": 1.2, "nano_shield": 1.0}
    )
    price = engine.calculate_price("plasma_rifle", quantity_demanded=10)
    assert price == 720.0

from dataclasses import dataclass
import math


@dataclass
class MenuItem:
    item_id: str = ""
    name: str = ""
    category: str = ""
    unit_cost: float = 0
    price: float = 0
    profit: float = 0

    def __post_init__(self):
        self.profit = self.price - self.unit_cost

    def validate_categories(self) -> None:
        if not self.item_id or not self.name or not self.category:
            raise ValueError("Missing required menu field.")
        
        if self.unit_cost < 0:
            raise ValueError("unit_cost cannot be negative.")
        
        if self.price < 0:
            raise ValueError("price cannot be negative.")

    def validate_numerical_fields(self, cost_str, price_str) -> None:
        # Check if they are indeed numerical values
        try:
            unit_cost = float(cost_str)
            price = float(price_str)
        except (TypeError, ValueError) as exc:
            raise ValueError("Non numerical cost or price.") from exc

        # Reject NaN and infinite monetary values
        if not math.isfinite(unit_cost) or not math.isfinite(price):
            raise ValueError("Cost and price must be finite numbers.")

        # Check if the values are in the expected ranges
        if unit_cost < 0 or price < 0:
            raise ValueError("Invalid cost or price range.")

        self.unit_cost = unit_cost
        self.price = price

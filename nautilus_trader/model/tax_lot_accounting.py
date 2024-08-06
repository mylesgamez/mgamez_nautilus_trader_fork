from decimal import Decimal

from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity


class TaxLot:
    def __init__(self, quantity: Quantity, price: Price, timestamp: int):
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp


class TaxLotAccounting:
    def __init__(self):
        self.positions = {}  # Dictionary to store tax lots for each position

    def add_tax_lot(self, position_id, tax_lot):
        if position_id not in self.positions:
            self.positions[position_id] = []
        self.positions[position_id].append(tax_lot)

    def get_tax_lots(self, position_id):
        return self.positions.get(position_id, [])

    def calculate_realized_pnl(self, position_id, sell_price, sell_quantity):
        tax_lots = self.positions.get(position_id, [])
        realized_pnl = Decimal("0")
        remaining_quantity = sell_quantity

        for lot in tax_lots[:]:
            if remaining_quantity == Quantity.zero():
                break

            if lot.quantity <= remaining_quantity:
                realized_pnl += (
                    sell_price.as_decimal() - lot.price.as_decimal()
                ) * lot.quantity.as_decimal()
                remaining_quantity -= lot.quantity
                tax_lots.remove(lot)
            else:
                realized_pnl += (
                    sell_price.as_decimal() - lot.price.as_decimal()
                ) * remaining_quantity.as_decimal()
                lot.quantity -= remaining_quantity
                remaining_quantity = Quantity.zero()

        self.positions[position_id] = tax_lots
        return realized_pnl

from datetime import date
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class OrderLine:
    """
    Value object to represent an order line requested by a customer

    Notes.
        1. Customers place orders
        2. An order is identified by an order reference and comprises multiple
        order lines where each line has a SKU (stock-keeping unit) and a quantity.
    """
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        """
        Entity to represent a batch ordered by the purchasing department

        Notes.
            1. The purchasing department orders small batches of stock
            2. A batch of stock has a unique ID called a reference, a SKU, and a quantity
            3. Customers can allocate an order line to buy items from this batch
        """
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty

    def allocate(self, line: OrderLine):
        self.available_quantity -= line.qty

    def can_allocate(self, line: OrderLine):
        return line.qty <= self.available_quantity
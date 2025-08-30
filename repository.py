import abc
import model

from sqlalchemy.sql import text


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        # Insert batch if it does not exist
        # Get lines IDs on _allocations
        # Insert tuple (batch_id, order_id) on allocations only if it does not exist
        ...

    def get(self, reference) -> model.Batch:
        [[reference, sku, _purchased_quantity, eta]] = self.session.execute(
            text(
                "SELECT reference, sku, _purchased_quantity, eta FROM batches"
                " WHERE reference=:reference"
            ),
            dict(reference=reference),
        )
        batch = model.Batch(reference, sku=sku, qty=_purchased_quantity, eta=eta)

        rows = list(
            self.session.execute(
                text(
                    "SELECT ol.orderid, ol.sku, ol.qty FROM order_lines AS ol"
                    " JOIN batches AS b ON b.sku = ol.sku"
                    " WHERE b.reference=:reference"
                ),
                dict(reference=batch.reference),
            )
        )
        batch._allocations = set(
            model.OrderLine(orderid=row[0], sku=row[1], qty=row[2]) for row in rows
        )
        return batch

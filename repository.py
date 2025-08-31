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

    def __insert_if_not_exists(self, table: str, data: dict):
        data_sanitized = {k: v for k, v in data.items() if v is not None}

        cols = ", ".join(data_sanitized.keys())
        placeholders = ", ".join([f":{k}" for k in data_sanitized.keys()])
        where_clause = " AND ".join([f"{k} = :{k}" for k in data_sanitized.keys()])

        self.session.execute(
            text(
                f"""
                INSERT INTO {table} ({cols})
                SELECT {placeholders}
                WHERE NOT EXISTS (
                    SELECT 1 FROM {table} WHERE {where_clause}
                )
                """
            ),
            data_sanitized,
        )

        row = self.session.execute(
            text(f"SELECT id FROM {table} WHERE {where_clause}"), data_sanitized
        ).fetchone()

        return row.id if row else None

    def add(self, batch):
        batch_id = self.__insert_if_not_exists(
            "batches",
            {
                "reference": batch.reference,
                "sku": batch.sku,
                "_purchased_quantity": batch._purchased_quantity,
                "eta": batch.eta,
            },
        )
        orderline_ids = [
            self.__insert_if_not_exists(
                "order_lines",
                {"sku": line.sku, "qty": line.qty, "orderid": line.orderid},
            )
            for line in batch._allocations
        ]
        for orderline_id in orderline_ids:
            self.__insert_if_not_exists(
                "allocations", {"batch_id": batch_id, "orderline_id": orderline_id}
            )

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

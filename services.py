from __future__ import annotations

import model
from model import OrderLine, Batch
from repository import AbstractRepository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref


def deallocate(orderid: str, sku: str, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(sku, batches):
        raise InvalidSku(f"Invalid sku {sku}")
    line = repo.get_line(orderid)
    batchref = model.deallocate(line, batches)
    session.commit()
    return batchref


def add_batch(batch: Batch, repo: AbstractRepository, session) -> None:
    repo.add(batch=batch)
    session.commit()

from datetime import date, timedelta
import pytest

from model import OrderLine, Batch, allocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty):
	# Fixture to create a batch and an order line
	return (
		Batch("batch-001", sku, batch_qty, eta=date.today()),
		OrderLine("order-123", sku, line_qty),
	)


def test_allocating_to_a_batch_reduces_the_available_quantity():
	large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
	large_batch.allocate(small_line)

	assert large_batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
	large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)

	assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
	small_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)

	assert not small_batch.can_allocate(small_line)


def test_can_allocate_if_available_equal_to_required():
	large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 1, 1)

	assert large_batch.can_allocate(small_line)


def test_prefers_warehouse_batches_to_shipments():
	in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
	shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
	line = OrderLine("oref", "RETRO-CLOCK", 10)
	
	allocate(line, [in_stock_batch, shipment_batch])

	assert in_stock_batch.available_quantity == 90
	assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
	earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
	medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
	latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
	line = OrderLine("order1", "MINIMALIST-SPOON", 10)
	
	allocate(line, [medium, earliest, latest])
	
	assert earliest.available_quantity == 90

def test_order_lines_equality():
	line1 = OrderLine("order-123", "SMALL-TABLE", 2)
	line2 = OrderLine("order-231", "SMALL-TABLE", 2)

	assert line1 is not line2


def test_batch_identity_equality():
	b1 = Batch("batch-001", "SMALL-CHAIR", 2, "2025-04-25")
	b2 = b1
	b2.allocate(OrderLine("order-123", "SMALL-CHAIR", 1))

	assert b2 is b1 and b1 is b2

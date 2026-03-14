import pytest

from algorithms import RMQ


def test_rmq_supports_min_queries_and_point_updates() -> None:
    rmq = RMQ([5, 2, 7, 1, 3])

    rmq.validate()

    assert len(rmq) == 5
    assert list(rmq) == [5, 2, 7, 1, 3]
    assert rmq.to_list() == [5, 2, 7, 1, 3]
    assert rmq[0] == 5
    assert rmq[-1] == 3
    assert rmq.query() == 1
    assert rmq.query(0, 3) == 2
    assert rmq.argmin() == 3
    assert rmq.argmin(0, 3) == 1
    assert rmq.query_with_index(1, 5) == (3, 1)

    rmq.update(3, 6)
    rmq.update(-1, 0)
    rmq.validate()

    assert rmq.to_list() == [5, 2, 7, 6, 0]
    assert rmq.query() == 0
    assert rmq.argmin() == 4
    assert rmq.query_with_index(1, 4) == (1, 2)


def test_rmq_breaks_ties_by_leftmost_index() -> None:
    rmq = RMQ([4, 1, 3, 1, 2])

    rmq.validate()

    assert rmq.query() == 1
    assert rmq.argmin() == 1
    assert rmq.query_with_index(2, 5) == (3, 1)


def test_rmq_raises_for_invalid_queries() -> None:
    rmq = RMQ([8, 6, 7])

    with pytest.raises(IndexError):
        rmq.update(3, 10)

    with pytest.raises(ValueError):
        rmq.query(1, 1)

    with pytest.raises(IndexError):
        rmq.query(-5, 2)

    empty = RMQ([])
    with pytest.raises(ValueError):
        empty.query()

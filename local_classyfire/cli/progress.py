from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

from tqdm import tqdm

T = TypeVar("T")


def progress_iter(
    iterable: Iterable[T],
    *,
    total: int | None = None,
    desc: str | None = None,
    unit: str = "item",
    enabled: bool = True,
) -> Iterator[T]:
    """Wrap iterable with tqdm when enabled."""

    if not enabled:
        yield from iterable
        return

    yield from tqdm(
        iterable,
        total=total,
        desc=desc,
        unit=unit,
    )
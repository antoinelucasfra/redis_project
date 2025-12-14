"""
Sushi Store - Redis-based inventory management system.

A demonstration project showcasing Redis capabilities for
high-performance stock management with Python.
"""

from .config import (
    ALL_INGREDIENTS,
    MAX_STOCK,
    REDIS_HOST,
    REDIS_PORT,
)
from .sushi_store import (
    buy_item,
    find_sushis_with_ingredients,
    generate_sushi_database,
    get_ingredients_info,
    get_inventory_info,
    get_redis_connection,
    load_sushis_to_redis,
    NoPlaceAvailableError,
    OutOfStockError,
    restock_item,
    TooMuchDemandError,
    TooMuchStockError,
)

__all__ = [
    # Config
    "ALL_INGREDIENTS",
    "MAX_STOCK",
    "REDIS_HOST",
    "REDIS_PORT",
    # Functions
    "buy_item",
    "find_sushis_with_ingredients",
    "generate_sushi_database",
    "get_ingredients_info",
    "get_inventory_info",
    "get_redis_connection",
    "load_sushis_to_redis",
    "restock_item",
    # Exceptions
    "NoPlaceAvailableError",
    "OutOfStockError",
    "TooMuchDemandError",
    "TooMuchStockError",
]

"""
Sushi Store - Redis-based inventory management system.
Core business logic for managing sushi stock and purchases.
"""

import random
import time

import pandas as pd
import redis

from .config import (
    ALL_INGREDIENTS,
    DEFAULT_SUSHI_COUNT,
    INGREDIENT_OPTIONS,
    MAX_INITIAL_STOCK,
    MAX_STOCK,
    MIN_INITIAL_STOCK,
    RANDOM_SEED,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class OutOfStockError(Exception):
    """Raised when requested sushi has no stock available."""
    pass


class TooMuchStockError(Exception):
    """Raised when stock is already at maximum capacity."""
    pass


class TooMuchDemandError(Exception):
    """Raised when customer demand exceeds available stock."""
    pass


class NoPlaceAvailableError(Exception):
    """Raised when restock would exceed maximum storage capacity."""
    pass


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

def get_redis_connection(
    host: str = REDIS_HOST,
    port: int = REDIS_PORT,
    db: int = REDIS_DB
) -> redis.Redis:
    """
    Create and return a Redis connection.

    Parameters
    ----------
    host : str
        Redis server hostname (default: 127.0.0.1)
    port : int
        Redis server port (default: 6379)
    db : int
        Redis database number (default: 0)

    Returns
    -------
    redis.Redis
        Connected Redis client instance
    """
    return redis.Redis(host=host, port=port, db=db)


# ============================================================================
# DATA GENERATION
# ============================================================================

def generate_sushi(sushi_id: int) -> dict:
    """
    Generate a single sushi with random ingredients.

    Parameters
    ----------
    sushi_id : int
        Unique identifier for the sushi

    Returns
    -------
    dict
        Sushi data with id, ingredients, stock, and purchase count
    """
    sushi = {'id': sushi_id}

    # Randomly assign each ingredient
    for ingredient in ALL_INGREDIENTS:
        sushi[ingredient] = random.choice(INGREDIENT_OPTIONS)

    # Add stock and purchase tracking
    sushi['stock'] = random.randint(MIN_INITIAL_STOCK, MAX_INITIAL_STOCK)
    sushi['nb_achat'] = 0

    return sushi


def generate_sushi_database(
    count: int = DEFAULT_SUSHI_COUNT,
    seed: int = RANDOM_SEED
) -> list[dict]:
    """
    Generate a list of random sushi configurations.

    Parameters
    ----------
    count : int
        Number of sushis to generate (default: 100,000)
    seed : int
        Random seed for reproducibility (default: 444)

    Returns
    -------
    list[dict]
        List of sushi dictionaries
    """
    random.seed(seed)

    start_time = time.perf_counter()
    sushis = [generate_sushi(i) for i in range(count)]
    elapsed = time.perf_counter() - start_time

    print(f"Generated {count:,} sushis in {elapsed:.2f} seconds")
    return sushis


def load_sushis_to_redis(r: redis.Redis, sushis: list[dict]) -> None:
    """
    Load sushi data into Redis using pipelining for efficiency.

    Parameters
    ----------
    r : redis.Redis
        Redis connection
    sushis : list[dict]
        List of sushi dictionaries to store
    """
    start_time = time.perf_counter()

    with r.pipeline() as pipe:
        for i, sushi in enumerate(sushis):
            key = f"sushi:{i}"
            pipe.hset(key, mapping=sushi)
        pipe.execute()

    elapsed = time.perf_counter() - start_time
    print(f"Loaded {len(sushis):,} sushis to Redis in {elapsed:.2f} seconds")


# ============================================================================
# STOCK MANAGEMENT
# ============================================================================

def buy_item(r: redis.Redis, sushi_id: str, count: int) -> None:
    """
    Purchase sushis, decreasing stock and increasing purchase count.

    Uses Redis transactions (WATCH/MULTI/EXEC) for atomic operations.

    Parameters
    ----------
    r : redis.Redis
        Redis connection
    sushi_id : str
        Sushi key (e.g., "sushi:5")
    count : int
        Number of sushis to purchase

    Raises
    ------
    OutOfStockError
        If sushi has no stock available
    TooMuchDemandError
        If demand exceeds available stock (partial purchase made)
    """
    with r.pipeline() as pipe:
        while True:
            pipe.watch(sushi_id)
            current_stock = int(r.hget(sushi_id, 'stock').decode())

            if current_stock >= count:
                # Normal purchase
                pipe.multi()
                pipe.hincrby(sushi_id, 'stock', -count)
                pipe.hincrby(sushi_id, 'nb_achat', count)
                pipe.execute()
                break

            elif current_stock > 0:
                # Partial purchase - buy all remaining
                pipe.multi()
                pipe.hset(sushi_id, 'stock', 0)
                pipe.hincrby(sushi_id, 'nb_achat', current_stock)
                pipe.execute()
                raise TooMuchDemandError(
                    f"Désolé, vous avez acheté tous les {sushi_id} restants "
                    f"({current_stock}) mais il n'y en avait pas autant que demandé ({count})"
                )
            else:
                # No stock available
                pipe.unwatch()
                raise OutOfStockError(f"Désolé, {sushi_id} est en rupture de stock!")


def restock_item(r: redis.Redis, sushi_id: str, count: int) -> None:
    """
    Restock sushis, increasing available inventory.

    Uses Redis transactions for atomic operations. Maximum stock is 10,000.

    Parameters
    ----------
    r : redis.Redis
        Redis connection
    sushi_id : str
        Sushi key (e.g., "sushi:9")
    count : int
        Number of sushis to add to stock

    Raises
    ------
    TooMuchStockError
        If stock is already at maximum
    NoPlaceAvailableError
        If restock would exceed maximum (partial restock made)
    """
    with r.pipeline() as pipe:
        while True:
            pipe.watch(sushi_id)
            current_stock = int(r.hget(sushi_id, 'stock').decode())

            if current_stock + count <= MAX_STOCK:
                # Full restock possible
                pipe.multi()
                pipe.hincrby(sushi_id, 'stock', count)
                pipe.execute()
                break

            elif current_stock < MAX_STOCK:
                # Partial restock - fill to max
                pipe.multi()
                pipe.hset(sushi_id, 'stock', MAX_STOCK)
                pipe.execute()
                raise NoPlaceAvailableError(
                    f"Stock de {sushi_id} rempli au maximum ({MAX_STOCK:,})"
                )
            else:
                # Already at max
                pipe.unwatch()
                raise TooMuchStockError(
                    f"{sushi_id} est déjà au stock maximum!"
                )


# ============================================================================
# DATA RETRIEVAL
# ============================================================================

def get_inventory_info(r: redis.Redis, sushi_count: int) -> pd.DataFrame:
    """
    Retrieve stock and purchase information for all sushis.

    Parameters
    ----------
    r : redis.Redis
        Redis connection
    sushi_count : int
        Total number of sushis in database

    Returns
    -------
    pd.DataFrame
        DataFrame with 'stock' and 'nb_achat' columns
    """
    data = []

    for i in range(sushi_count):
        key = f"sushi:{i}"
        stock = int(r.hget(key, 'stock').decode())
        nb_achat = int(r.hget(key, 'nb_achat').decode())
        data.append({'stock': stock, 'nb_achat': nb_achat})

    return pd.DataFrame(
        data,
        index=[f"sushi:{i}" for i in range(sushi_count)]
    )


def get_ingredients_info(r: redis.Redis, sushi_count: int) -> pd.DataFrame:
    """
    Retrieve ingredient information for all sushis.

    Parameters
    ----------
    r : redis.Redis
        Redis connection
    sushi_count : int
        Total number of sushis in database

    Returns
    -------
    pd.DataFrame
        DataFrame with ingredient columns (73 total)
    """
    data = []

    for i in range(sushi_count):
        key = f"sushi:{i}"
        row = {}
        for ingredient in ALL_INGREDIENTS:
            row[ingredient] = r.hget(key, ingredient).decode()
        data.append(row)

    return pd.DataFrame(
        data,
        index=[f"sushi:{i}" for i in range(sushi_count)]
    )


def find_sushis_with_ingredients(
    ingredient_df: pd.DataFrame,
    required_ingredients: list[str]
) -> list[int]:
    """
    Find sushis containing all specified ingredients.

    Parameters
    ----------
    ingredient_df : pd.DataFrame
        DataFrame with ingredient information (from get_ingredients_info)
    required_ingredients : list[str]
        List of ingredient names that must all be present

    Returns
    -------
    list[int]
        List of sushi indices matching all criteria
    """
    matches = []

    for idx in range(len(ingredient_df)):
        row = ingredient_df.iloc[idx]
        if all(row[ing] == 'Oui' for ing in required_ingredients):
            matches.append(idx)

    if matches:
        sushi_names = [f"sushi:{i}" for i in matches]
        print(f"Vous pourriez apprécier les sushis suivants : {', '.join(sushi_names)}")
    else:
        print("Aucun sushi ne correspond à vos critères.")

    return matches

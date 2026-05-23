from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable

import numpy as np
import pandas as pd
from faker import Faker

fake = Faker()

CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar", "Quetta", "Hyderabad", "Sukkur", "Sialkot", "Gujranwala"]
REGIONS = ["North", "South", "East", "West", "Central", "International"]
CATEGORIES = ["Premium", "Standard", "Budget", "Enterprise", "Basic", "Gold", "Silver", "Bronze"]
STATUS_VALUES = ["Active", "Pending", "Completed", "Cancelled", "Under Review", "Delayed", "Closed"]
RISK_BANDS = ["Low", "Medium", "High", "Critical"]
PAYMENT_METHODS = ["Cash", "Card", "Bank Transfer", "Mobile Wallet", "COD", "Cheque"]
WEATHER_VALUES = ["Clear", "Cloudy", "Rain", "Storm", "Fog", "Haze", "Windy"]
ROAD_TYPES = ["Highway", "Main Road", "Service Road", "Bridge", "Tunnel", "Residential Street"]
TRANSPORT_MODES = ["Road", "Rail", "Air", "Sea", "Courier"]


def date_range_values(n: int, rng: np.random.Generator, include_time: bool = True) -> pd.Series:
    start = datetime(2023, 1, 1)
    minutes = rng.integers(0, 365 * 24 * 60, size=n)
    values = [start + timedelta(minutes=int(m)) for m in minutes]
    if include_time:
        return pd.Series([v.strftime("%Y-%m-%d %H:%M:%S") for v in values])
    return pd.Series([v.strftime("%Y-%m-%d") for v in values])


def generate_id(prefix: str, start: int, n: int) -> pd.Series:
    return pd.Series([f"{prefix}{i:08d}" for i in range(start, start + n)])


def random_choice(values: Iterable[str], n: int, rng: np.random.Generator) -> pd.Series:
    values = list(values)
    idx = rng.integers(0, len(values), size=n)
    return pd.Series([values[i] for i in idx])


def generate_column(name: str, data_type: str, n: int, rng: np.random.Generator, row_start: int, domain_key: str) -> pd.Series:
    lower = name.lower()

    if data_type == "ID" or lower.endswith("_id") or "id" == lower:
        prefix = ''.join([part[0] for part in lower.split('_') if part])[:4].upper() or "ID"
        return generate_id(prefix, row_start + 1, n)

    if data_type == "DateTime" or "timestamp" in lower or "datetime" in lower:
        return date_range_values(n, rng, include_time=True)

    if data_type == "Date" or lower.endswith("_date"):
        return date_range_values(n, rng, include_time=False)

    if data_type == "Geographic":
        if "longitude" in lower or lower in {"lng", "long"}:
            return pd.Series(rng.uniform(60.0, 78.0, size=n).round(6))
        return pd.Series(rng.uniform(24.0, 37.0, size=n).round(6))

    if data_type == "Binary" or lower.endswith("_flag"):
        p = 0.18 if any(x in lower for x in ["return", "default", "fraud", "damage", "cancel", "accident"]) else 0.5
        return pd.Series(rng.choice([0, 1], size=n, p=[1 - p, p]))

    if data_type == "Percent":
        if "discount" in lower:
            return pd.Series(rng.uniform(0, 0.45, size=n).round(4))
        if "margin" in lower:
            return pd.Series(rng.uniform(0.05, 0.55, size=n).round(4))
        if "attendance" in lower or "load_factor" in lower or "humidity" in lower:
            return pd.Series(rng.uniform(0.45, 0.99, size=n).round(4))
        return pd.Series(rng.uniform(0.01, 0.95, size=n).round(4))

    if data_type == "Accounting":
        if any(x in lower for x in ["income", "salary"]):
            return pd.Series(rng.normal(120_000, 45_000, size=n).clip(20_000, 500_000).round(2))
        if any(x in lower for x in ["price", "amount", "sales", "revenue", "cost", "value", "rent", "loan"]):
            return pd.Series(rng.lognormal(10, 0.75, size=n).clip(500, 15_000_000).round(2))
        return pd.Series(rng.lognormal(9, 0.9, size=n).clip(100, 10_000_000).round(2))

    if data_type == "Number":
        if "age" in lower:
            return pd.Series(rng.integers(18, 75, size=n))
        if "score" in lower:
            return pd.Series(rng.integers(300 if "credit" in lower else 0, 850 if "credit" in lower else 101, size=n))
        if "quantity" in lower or "count" in lower:
            return pd.Series(rng.integers(1, 25, size=n))
        if "months" in lower:
            return pd.Series(rng.integers(1, 84, size=n))
        return pd.Series(rng.integers(0, 1000, size=n))

    if data_type == "Decimal":
        if "temperature" in lower:
            return pd.Series(rng.normal(28, 8, size=n).round(2))
        if "speed" in lower:
            return pd.Series(rng.normal(55, 18, size=n).clip(0, 180).round(2))
        if "distance" in lower:
            return pd.Series(rng.lognormal(3.3, 0.7, size=n).clip(0.5, 3500).round(2))
        if "rating" in lower:
            return pd.Series(rng.uniform(1, 5, size=n).round(1))
        if "delay" in lower or "duration" in lower:
            return pd.Series(rng.exponential(20, size=n).clip(0, 480).round(2))
        return pd.Series(rng.normal(100, 35, size=n).round(2))

    if data_type == "Categorical":
        if "city" in lower:
            return random_choice(CITIES, n, rng)
        if "region" in lower:
            return random_choice(REGIONS, n, rng)
        if "status" in lower:
            return random_choice(STATUS_VALUES, n, rng)
        if "risk" in lower:
            return random_choice(RISK_BANDS, n, rng)
        if "payment" in lower:
            return random_choice(PAYMENT_METHODS, n, rng)
        if "weather" in lower:
            return random_choice(WEATHER_VALUES, n, rng)
        if "road" in lower:
            return random_choice(ROAD_TYPES, n, rng)
        if "transport" in lower:
            return random_choice(TRANSPORT_MODES, n, rng)
        return random_choice(CATEGORIES, n, rng)

    # Text fallback.
    if "name" in lower:
        return pd.Series([fake.company() for _ in range(n)])
    if "email" in lower:
        return pd.Series([fake.email() for _ in range(n)])
    if "notes" in lower or "description" in lower:
        phrases = ["requires review", "normal record", "priority item", "manual check", "clean sample", "student practice case"]
        return random_choice(phrases, n, rng)
    return pd.Series([fake.word().title() for _ in range(n)])

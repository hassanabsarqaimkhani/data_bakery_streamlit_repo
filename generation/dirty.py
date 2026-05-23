from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from app_config import DIRT_INTENSITIES


def _pick_indices(n: int, pct: float, rng: np.random.Generator) -> np.ndarray:
    k = max(1, int(n * pct)) if n else 0
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=int)
    return rng.choice(n, size=k, replace=False)


def _as_object(series: pd.Series) -> pd.Series:
    return series.astype("object").copy()


def inject_column_dirt(series: pd.Series, data_type: str, dirt_types: List[str], intensity: str, rng: np.random.Generator) -> Tuple[pd.Series, List[str]]:
    if not dirt_types:
        return series, []
    pct = DIRT_INTENSITIES.get(intensity, 0.075)
    s = _as_object(series)
    applied: List[str] = []
    n = len(s)

    for dirt in dirt_types:
        idx = _pick_indices(n, pct, rng)
        if len(idx) == 0:
            continue

        if dirt == "Missing values and blank cells":
            s.iloc[idx] = ""
        elif dirt == "Leading and trailing white spaces":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: f"  {v}   ")
        elif dirt == "Mixed letter casing":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: v.upper() if len(v) % 2 else v.lower())
        elif dirt == "Typographical errors and misspellings":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: _typo(v))
        elif dirt == "Inconsistent date formats":
            s.iloc[idx] = s.iloc[idx].astype(str).map(_date_variant)
        elif dirt == "Invalid or impossible numeric values":
            if data_type in {"Number", "Decimal", "Accounting", "Percent", "Geographic"}:
                s.iloc[idx] = rng.choice([-999, -1, 999999999, "ERROR", "N/A"], size=len(idx))
        elif dirt == "Special characters and emojis in text fields":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: f"{v} ✨")
        elif dirt == "Inconsistent categorical labels":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: _category_variant(v))
        elif dirt == "Delimiter collisions in raw text":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: f"{v}, extra|field")
        elif dirt == "Trailing or leading zeros treated inconsistently":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: f"00{v}")
        elif dirt == "Hardcoded placeholders or error codes":
            s.iloc[idx] = rng.choice(["N/A", "UNKNOWN", "TBD", "#ERROR", "-999"], size=len(idx))
        elif dirt == "Out-of-bounds geographic coordinates":
            if data_type == "Geographic":
                s.iloc[idx] = rng.choice([999, -999, 181, -181, 9999], size=len(idx))
        elif dirt == "Hidden non-printing control characters":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: f"{v}\u200b")
        elif dirt == "Skewed timezones across timestamps":
            s.iloc[idx] = s.iloc[idx].astype(str).map(lambda v: f"{v}+05:00" if "+" not in v else v)
        elif dirt == "Duplicate records":
            # Handled at dataframe level.
            pass
        applied.append(dirt)

    return s, applied


def inject_dataframe_dirt(df: pd.DataFrame, selected_columns, intensity: str, rng: np.random.Generator) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    report: Dict[str, List[str]] = {}
    for col in selected_columns:
        if col.final_name not in df.columns:
            continue
        modified, applied = inject_column_dirt(df[col.final_name], col.data_type, col.dirt_types, intensity, rng)
        df[col.final_name] = modified
        if applied:
            report[col.final_name] = applied

    if any("Duplicate records" in col.dirt_types for col in selected_columns) and len(df) > 2:
        pct = DIRT_INTENSITIES.get(intensity, 0.075)
        count = max(1, int(len(df) * min(pct, 0.12)))
        target_idx = rng.choice(len(df), size=count, replace=False)
        source_idx = np.maximum(target_idx - 1, 0)
        df.iloc[target_idx] = df.iloc[source_idx].values
        report["__record_level__"] = report.get("__record_level__", []) + ["Duplicate records"]
    return df, report


def _typo(value: str) -> str:
    if len(value) < 3:
        return value + "x"
    return value[:1] + value[2:3] + value[1:2] + value[3:]


def _date_variant(value: str) -> str:
    # Handles clean YYYY-MM-DD or YYYY-MM-DD HH:MM:SS strings.
    date_part = value.split(" ")[0]
    parts = date_part.split("-")
    if len(parts) != 3:
        return value
    y, m, d = parts
    return f"{d}/{m}/{y}"


def _category_variant(value: str) -> str:
    if not value:
        return value
    variants = [value.lower(), value.upper(), value.replace(" ", "_"), f"{value} ", f"{value[:3]}"]
    return variants[len(value) % len(variants)]

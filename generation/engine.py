from __future__ import annotations

import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from app_config import CHUNK_SIZE, OUTPUT_ROOT_NAME, TEMP_ROOT
from core.models import GenerationPlan
from domains.registry import get_domain
from export.pdf_exporter import create_all_pdfs
from generation.dirty import inject_dataframe_dirt
from generation.values import generate_column

ProgressCallback = Optional[Callable[[str, float], None]]


def _progress(callback: ProgressCallback, message: str, value: float) -> None:
    if callback:
        callback(message, value)


def generate_preview(plan: GenerationPlan, rows: int = 100) -> pd.DataFrame:
    rng = np.random.default_rng(plan.random_seed)
    df = _generate_chunk(plan, rows, 0, rng, apply_dirty=True)[0]
    return df


def generate_package(plan: GenerationPlan, progress_callback: ProgressCallback = None) -> Tuple[Path, Dict[str, List[str]]]:
    session_dir = Path(tempfile.mkdtemp(prefix="data_bakery_", dir=TEMP_ROOT))
    output_dir = session_dir / OUTPUT_ROOT_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(plan.random_seed)
    dirt_report: Dict[str, List[str]] = {}

    _progress(progress_callback, "Preparing generation recipe...", 0.03)
    time.sleep(0.1)

    if plan.dataset_type_key == "relational_multitable":
        _generate_relational_package(plan, output_dir, rng, dirt_report, progress_callback)
    else:
        csv_path = output_dir / "dataset.csv"
        rows_written = 0
        first = True
        while rows_written < plan.rows:
            n = min(CHUNK_SIZE, plan.rows - rows_written)
            chunk, chunk_report = _generate_chunk(plan, n, rows_written, rng, apply_dirty=True)
            for k, v in chunk_report.items():
                dirt_report.setdefault(k, [])
                for item in v:
                    if item not in dirt_report[k]:
                        dirt_report[k].append(item)
            chunk.to_csv(csv_path, mode="w" if first else "a", header=first, index=False, encoding="utf-8-sig")
            rows_written += n
            first = False
            _progress(progress_callback, f"Writing dataset.csv: {rows_written:,} of {plan.rows:,} rows...", 0.08 + 0.66 * rows_written / plan.rows)

    _progress(progress_callback, "Creating PDF documentation...", 0.80)
    create_all_pdfs(plan, get_domain(plan.dataset_type_key), output_dir, dirt_report)

    _progress(progress_callback, "Packaging downloadable ZIP...", 0.92)
    zip_path = session_dir / f"Data_Bakery_Output_{int(time.time())}.zip"
    _zip_output(output_dir, zip_path)
    _progress(progress_callback, "Package ready for immediate download.", 1.0)
    return zip_path, dirt_report


def _generate_chunk(plan: GenerationPlan, n: int, row_start: int, rng: np.random.Generator, apply_dirty: bool = True):
    data = {}
    for col in plan.columns:
        data[col.final_name] = generate_column(col.final_name, col.data_type, n, rng, row_start, plan.dataset_type_key)
    df = pd.DataFrame(data)
    df = _apply_simple_relationships(df, plan, rng)
    report: Dict[str, List[str]] = {}
    if apply_dirty:
        df, report = inject_dataframe_dirt(df, plan.columns, plan.dirt_intensity, rng)
    return df, report


def _apply_simple_relationships(df: pd.DataFrame, plan: GenerationPlan, rng: np.random.Generator) -> pd.DataFrame:
    cols = set(df.columns)
    if {"quantity", "unit_price"}.issubset(cols):
        quantity = pd.to_numeric(df["quantity"], errors="coerce").fillna(1)
        unit_price = pd.to_numeric(df["unit_price"], errors="coerce").fillna(100)
        if "gross_sales_amount" in cols:
            df["gross_sales_amount"] = (quantity * unit_price).round(2)
        if "discount_percent" in cols and "net_sales_amount" in cols:
            discount = pd.to_numeric(df["discount_percent"], errors="coerce").fillna(0)
            df["net_sales_amount"] = (quantity * unit_price * (1 - discount)).round(2)
    if {"monthly_income", "existing_debt_amount"}.issubset(cols) and "debt_to_income_ratio" in cols:
        income = pd.to_numeric(df["monthly_income"], errors="coerce").replace(0, 1).fillna(1)
        debt = pd.to_numeric(df["existing_debt_amount"], errors="coerce").fillna(0)
        df["debt_to_income_ratio"] = (debt / income).clip(0, 2).round(4)
    if {"credit_score", "approval_status"}.issubset(cols):
        scores = pd.to_numeric(df["credit_score"], errors="coerce").fillna(600)
        df["approval_status"] = np.where(scores > 700, "Approved", np.where(scores < 550, "Rejected", "Manual Review"))
    if {"scheduled_departure_timestamp", "actual_departure_timestamp", "delay_minutes"}.issubset(cols):
        delays = pd.to_numeric(df["delay_minutes"], errors="coerce").fillna(0).astype(float)
        scheduled = pd.to_datetime(df["scheduled_departure_timestamp"], errors="coerce")
        actual = scheduled + pd.to_timedelta(delays, unit="m")
        df["actual_departure_timestamp"] = actual.dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def _generate_relational_package(plan: GenerationPlan, output_dir: Path, rng: np.random.Generator, dirt_report: Dict[str, List[str]], progress_callback: ProgressCallback):
    total_order_items = plan.rows
    customer_count = max(5_000, plan.rows // 25)
    product_count = 1_000
    order_count = max(20_000, plan.rows // 3)

    def write_simple(name, rows, cols):
        sub_cols = [col for col in plan.columns if col.final_name in cols]
        sub_plan = GenerationPlan(
            dataset_type_key=plan.dataset_type_key,
            dataset_type_name=plan.dataset_type_name,
            learning_objective=plan.learning_objective,
            rows=rows,
            columns=sub_cols or plan.columns[:min(8, len(plan.columns))],
            dirt_intensity=plan.dirt_intensity,
            question_answers=plan.question_answers,
            random_seed=plan.random_seed,
        )
        first = True
        written = 0
        path = output_dir / name
        while written < rows:
            n = min(CHUNK_SIZE, rows - written)
            df, report = _generate_chunk(sub_plan, n, written, rng, apply_dirty=True)
            df.to_csv(path, mode="w" if first else "a", header=first, index=False, encoding="utf-8-sig")
            written += n
            first = False
            for k, v in report.items():
                dirt_report.setdefault(k, [])
                for item in v:
                    if item not in dirt_report[k]:
                        dirt_report[k].append(item)

    write_simple("customers.csv", customer_count, {"customer_id", "customer_segment", "customer_city", "region", "loyalty_member_flag"})
    _progress(progress_callback, "Created customers.csv...", 0.20)
    write_simple("products.csv", product_count, {"product_id", "product_category", "product_subcategory", "supplier_id", "unit_price"})
    _progress(progress_callback, "Created products.csv...", 0.32)
    write_simple("orders.csv", order_count, {"order_id", "customer_id", "order_timestamp", "payment_status", "delivery_status", "region"})
    _progress(progress_callback, "Created orders.csv...", 0.46)
    write_simple("order_items.csv", total_order_items, {"order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent", "line_total", "return_flag"})
    _progress(progress_callback, "Created order_items.csv...", 0.70)
    write_simple("payments.csv", max(20_000, order_count), {"payment_id", "order_id", "payment_method", "payment_status", "line_total"})
    _progress(progress_callback, "Created payments.csv...", 0.78)


def _zip_output(output_dir: Path, zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in sorted(output_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(output_dir.parent))


def cleanup_session_file(zip_path: Path) -> None:
    try:
        session_dir = zip_path.parent
        if session_dir.exists() and session_dir.name.startswith("data_bakery_"):
            shutil.rmtree(session_dir, ignore_errors=True)
    except Exception:
        pass


def cleanup_stale_temp_dirs(max_age_seconds: int = 3600) -> int:
    now = time.time()
    removed = 0
    for path in TEMP_ROOT.glob("data_bakery_*"):
        try:
            age = now - path.stat().st_mtime
            if age > max_age_seconds:
                shutil.rmtree(path, ignore_errors=True)
                removed += 1
        except Exception:
            continue
    return removed

from typing import List

from app_config import COLUMN_MAX, COLUMN_MIN, ROW_MAX, ROW_MIN
from core.models import GenerationPlan, SelectedColumn


class ValidationError(ValueError):
    pass


def validate_rows_columns(rows: int, columns: int) -> List[str]:
    warnings: List[str] = []
    if rows < ROW_MIN or rows > ROW_MAX:
        raise ValidationError(f"Rows must be between {ROW_MIN:,} and {ROW_MAX:,}.")
    if columns < COLUMN_MIN or columns > COLUMN_MAX:
        raise ValidationError(f"Columns must be between {COLUMN_MIN} and {COLUMN_MAX}.")
    if rows >= 540_000:
        warnings.append("You are generating near the maximum row range. Download size and generation time will increase.")
    return warnings


def validate_selected_columns(columns: List[SelectedColumn]) -> None:
    if not columns:
        raise ValidationError("At least one column must be selected.")
    names = [c.final_name.strip() for c in columns]
    if any(not n for n in names):
        raise ValidationError("Column names cannot be blank.")
    if len(set(names)) != len(names):
        raise ValidationError("Column names must be unique.")


def validate_plan(plan: GenerationPlan) -> List[str]:
    warnings = validate_rows_columns(plan.rows, plan.column_count)
    validate_selected_columns(plan.columns)
    if "Time-Series" in plan.learning_objective and not any(c.data_type == "DateTime" for c in plan.columns):
        warnings.append("Time-Series Analysis works best with at least one DateTime column.")
    if "Geospatial" in plan.learning_objective and not any(c.data_type == "Geographic" for c in plan.columns):
        warnings.append("Geospatial Analysis works best with latitude/longitude or another geographic field.")
    if "Financial" in plan.learning_objective and not any(c.data_type in {"Accounting", "Decimal", "Percent"} for c in plan.columns):
        warnings.append("Financial Analysis works best with accounting, decimal, or percent columns.")
    return warnings

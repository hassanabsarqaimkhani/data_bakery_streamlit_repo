from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ColumnSpec:
    name: str
    definition: str
    data_type: str
    role: str = "feature"
    allowed_dirt: List[str] = field(default_factory=list)


@dataclass
class DomainSpec:
    key: str
    name: str
    description: str
    columns: List[ColumnSpec]
    questions: List[str]
    dashboard_guidance: List[str]
    recommended_min_columns: int = 10


@dataclass
class SelectedColumn:
    original_name: str
    final_name: str
    definition: str
    data_type: str
    dirt_types: List[str] = field(default_factory=list)


@dataclass
class GenerationPlan:
    dataset_type_key: str
    dataset_type_name: str
    learning_objective: str
    rows: int
    columns: List[SelectedColumn]
    dirt_intensity: str
    question_answers: Dict[str, bool]
    random_seed: int
    output_folder_label: str = "Data_Bakery_Output"
    generated_by: str = "Data Bakery by Hassan Absar"
    powered_by: str = "Powered by STT Solutions"

    @property
    def column_count(self) -> int:
        return len(self.columns)

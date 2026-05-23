from core.models import GenerationPlan, SelectedColumn
from domains.registry import get_domain_by_name
from generation.engine import generate_preview


def test_preview_generation():
    domain = get_domain_by_name("E-Commerce & Retail Transactions")
    cols = [SelectedColumn(c.name, c.name, c.definition, c.data_type, []) for c in domain.columns[:8]]
    plan = GenerationPlan(
        dataset_type_key=domain.key,
        dataset_type_name=domain.name,
        learning_objective="Data Cleaning + Visualization",
        rows=500000,
        columns=cols,
        dirt_intensity="Medium",
        question_answers={q: True for q in domain.questions[:3]},
        random_seed=123,
    )
    df = generate_preview(plan, rows=25)
    assert df.shape == (25, 8)

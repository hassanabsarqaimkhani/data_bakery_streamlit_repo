from __future__ import annotations

import random
from pathlib import Path

import streamlit as st

from app_config import (
    APP_NAME,
    COLUMN_DEFAULT,
    COLUMN_MAX,
    COLUMN_MIN,
    DIRT_INTENSITIES,
    LEARNING_OBJECTIVES,
    POWERED_BY,
    PREVIEW_ROWS,
    ROW_DEFAULT,
    ROW_MAX,
    ROW_MIN,
    TARGET_URL,
    TYPE_COMPATIBLE_DIRT,
)
from core.models import GenerationPlan, SelectedColumn
from core.validators import ValidationError, validate_plan, validate_rows_columns
from domains.registry import get_domain_by_name, list_domains
from generation.engine import cleanup_session_file, cleanup_stale_temp_dirs, generate_package, generate_preview
from ui_styles import hero, inject_css, kpi_cards, section_title, sidebar_brand, stt_strip

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🍞",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
cleanup_stale_temp_dirs(max_age_seconds=3600)

with st.sidebar:
    sidebar_brand()
    st.markdown(f"### {APP_NAME}")
    st.caption(POWERED_BY)
    st.divider()
    st.markdown("**Target URL**")
    st.code(TARGET_URL)
    st.markdown("**Recipe Limits**")
    st.caption(f"Rows: {ROW_MIN:,}–{ROW_MAX:,}")
    st.caption(f"Columns: {COLUMN_MIN}–{COLUMN_MAX}")
    st.markdown("**Output Rule**")
    st.caption("Temporary server generation. Immediate ZIP download. CSV datasets + PDF documentation only.")
    st.divider()
    if st.button("Clean temporary generated files", use_container_width=True):
        removed = cleanup_stale_temp_dirs(max_age_seconds=0)
        zip_path = st.session_state.get("zip_path")
        if zip_path:
            cleanup_session_file(Path(zip_path))
            st.session_state.pop("zip_path", None)
            st.session_state.pop("zip_bytes", None)
        st.success(f"Temporary cleanup completed. Removed {removed} stale session folder(s).")

hero()
stt_strip()
kpi_cards()
st.divider()

# Session defaults.
if "seed" not in st.session_state:
    st.session_state.seed = random.randint(100000, 999999)
if "selected_column_names" not in st.session_state:
    st.session_state.selected_column_names = []

all_domains = list_domains()
domain_names = [d.name for d in all_domains]

setup_tab, schema_tab, generate_tab = st.tabs(["01 / Recipe Lab", "02 / Schema + Dirt Studio", "03 / Preview + Bake"])

with setup_tab:
    section_title(
        "Recipe Lab",
        "Build the dataset generation recipe.",
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        rows = st.number_input(
            "Rows",
            min_value=ROW_MIN,
            max_value=ROW_MAX,
            value=ROW_DEFAULT,
            step=10_000,
            help="Final hosted Streamlit range: 500,000 to 550,000 rows.",
        )
    with col2:
        column_count = st.number_input(
            "Columns",
            min_value=COLUMN_MIN,
            max_value=COLUMN_MAX,
            value=COLUMN_DEFAULT,
            step=1,
            help="Recipe column limit is locked at 5 to 25 columns.",
        )
    with col3:
        dirt_intensity = st.selectbox("Dirty Data Intensity", list(DIRT_INTENSITIES.keys()), index=1)

    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        domain_name = st.selectbox("Dataset Type", domain_names, index=0)
    with c2:
        learning_objective = st.selectbox("Learning Objective", LEARNING_OBJECTIVES, index=2)

    seed = st.number_input("Random Seed", min_value=1, max_value=999999999, value=int(st.session_state.seed), step=1)
    st.session_state.seed = int(seed)

    try:
        warnings = validate_rows_columns(int(rows), int(column_count))
        for warning in warnings:
            st.warning(warning)
    except ValidationError as exc:
        st.error(str(exc))

    domain = get_domain_by_name(domain_name)
    section_title("Domain Intelligence")
    st.info(domain.description)

with schema_tab:
    domain = get_domain_by_name(domain_name)
    candidate_names = [col.name for col in domain.columns]
    if not st.session_state.selected_column_names or set(st.session_state.selected_column_names) - set(candidate_names):
        st.session_state.selected_column_names = candidate_names[: int(column_count)]

    section_title(
        "AI-Suggested Candidate Columns",
        "The app proposes a domain-relevant column pool. Select the exact final schema for the recipe. The app will not exceed the 5–25 column limit.",
    )
    selected_names = st.multiselect(
        "Final Columns",
        options=candidate_names,
        default=st.session_state.selected_column_names[: int(column_count)],
        max_selections=int(column_count),
        help="Select exactly the number of columns requested in the recipe.",
    )
    st.session_state.selected_column_names = selected_names

    selected_columns = []
    section_title(
        "Column Configuration Studio",
        "Tune each column name, data type, and dirty-data recipe. Dirt options are filtered by data type to keep the generated data realistic and Power Query-cleanable.",
    )
    for spec in domain.columns:
        if spec.name not in selected_names:
            continue
        with st.expander(f"{spec.name} — {spec.definition}", expanded=False):
            c1, c2 = st.columns([1, 1])
            with c1:
                final_name = st.text_input("Column Name", value=spec.name, key=f"name_{spec.name}")
                data_type = st.selectbox(
                    "Data Type",
                    options=list(TYPE_COMPATIBLE_DIRT.keys()),
                    index=list(TYPE_COMPATIBLE_DIRT.keys()).index(spec.data_type),
                    key=f"type_{spec.name}",
                )
            with c2:
                compatible = TYPE_COMPATIBLE_DIRT.get(data_type, [])
                dirt_types = st.multiselect("Dirty Data Options", options=compatible, default=[], key=f"dirt_{spec.name}")
            st.caption(spec.definition)
            selected_columns.append(SelectedColumn(spec.name, final_name.strip(), spec.definition, data_type, dirt_types))

    st.session_state.selected_columns_for_plan = selected_columns

    section_title(
        "Contextual Yes / No Logic",
        "These controls are not decorative. They influence generated relationships, PDF explanations, and dashboard suggestions.",
    )
    question_answers = {}
    for i, q in enumerate(domain.questions[:6]):
        question_answers[q] = st.toggle(q, value=True if i < 3 else False, key=f"q_{domain.key}_{i}")
    st.session_state.question_answers = question_answers

with generate_tab:
    section_title(
        "Preview + Bake",
        "Generate a 100-row preview first, then bake the full temporary package and download the ZIP immediately.",
    )
    selected_columns = st.session_state.get("selected_columns_for_plan", [])
    question_answers = st.session_state.get("question_answers", {})
    plan = GenerationPlan(
        dataset_type_key=domain.key,
        dataset_type_name=domain.name,
        learning_objective=learning_objective,
        rows=int(rows),
        columns=selected_columns,
        dirt_intensity=dirt_intensity,
        question_answers=question_answers,
        random_seed=int(seed),
    )

    try:
        plan_warnings = validate_plan(plan)
        if plan.column_count != int(column_count):
            st.warning(f"You selected {plan.column_count} column(s). Your recipe asks for {int(column_count)} column(s).")
        for warning in plan_warnings:
            st.warning(warning)
    except ValidationError as exc:
        st.error(str(exc))

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Generate 100-row Preview", use_container_width=True):
            try:
                preview = generate_preview(plan, PREVIEW_ROWS)
                st.session_state.preview_df = preview
            except Exception as exc:
                st.error(f"Preview failed: {exc}")
    with c2:
        bake_clicked = st.button("Bake Dataset Package", use_container_width=True)

    if "preview_df" in st.session_state:
        st.dataframe(st.session_state.preview_df, use_container_width=True, height=380)

    if bake_clicked:
        try:
            validate_plan(plan)
            old_zip = st.session_state.get("zip_path")
            if old_zip:
                cleanup_session_file(Path(old_zip))
                st.session_state.pop("zip_path", None)
                st.session_state.pop("zip_bytes", None)

            progress = st.progress(0)
            status = st.empty()

            def update(message: str, value: float):
                status.info(message)
                progress.progress(min(1.0, max(0.0, value)))

            zip_path, dirt_report = generate_package(plan, update)
            st.session_state.zip_path = str(zip_path)
            st.session_state.dirt_report = dirt_report
            with open(zip_path, "rb") as f:
                st.session_state.zip_bytes = f.read()
            status.success("Your STT Solutions branded Data Bakery package is ready. Download immediately, then delete temporary server files.")
        except Exception as exc:
            st.error(f"Generation failed: {exc}")

    if st.session_state.get("zip_bytes"):
        st.success("Download package ready.")
        st.download_button(
            label="Download Data Bakery Output ZIP",
            data=st.session_state.zip_bytes,
            file_name="HassanAbsarSTTSolutionsDataBakeryOutput.zip",
            mime="application/zip",
            use_container_width=True,
        )
        st.caption("Streamlit does not provide a guaranteed browser event after download completion. Use the cleanup button after downloading; stale files are also removed automatically.")
        if st.button("I have downloaded — delete temporary server files now", use_container_width=True):
            zip_path = st.session_state.get("zip_path")
            if zip_path:
                cleanup_session_file(Path(zip_path))
            st.session_state.pop("zip_path", None)
            st.session_state.pop("zip_bytes", None)
            st.success("Temporary files deleted for this session.")
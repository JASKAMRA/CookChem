"""Two additive Streamlit pages; existing research pages remain unchanged."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Callable
from urllib.parse import urlparse

import plotly.graph_objects as go
import streamlit as st

from extension_data import DESIGNS, error_metrics, load_reconstruction_errors, load_stageb_finalized
from presentation import show_dataframe

DESIGN_LABELS = {"molecular_grouped": "Molecular-grouped", "source_held_out": "DOI-held-out"}
COLORS = {"molecular_grouped": "#2D5A27", "source_held_out": "#C85A32"}


def _fmt(value: float) -> str:
    return f"{value:,.2f}"


def _error_group_rows(rows: list[dict], field: str, minimum: int) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row[field] or "(not recorded)"].append(row)
    return sorted(({
        "Group": name, "Observations": len(group),
        "MAE (ACR pp)": round(sum(row["absolute_error"] for row in group) / len(group), 2),
        "Mean residual (ACR pp)": round(sum(row["residual"] for row in group) / len(group), 2),
    } for name, group in groups.items() if len(group) >= minimum),
        key=lambda row: row["MAE (ACR pp)"], reverse=True)


def _observation_table(rows: list[dict], limit: int | None = None) -> list[dict]:
    selected = rows[:limit] if limit else rows
    return [{
        "Observation ID": row["observation_id"], "Compound": row["compound"],
        "Food matrix": row["food_matrix"], "DOI": row["doi"], "Fold": row["fold"],
        "Actual ACR (%)": round(row["actual"], 2), "Predicted ACR (%)": round(row["predicted"], 2),
        "Residual (pp)": round(row["residual"], 2), "Absolute error (pp)": round(row["absolute_error"], 2),
        "Source locator": row["source_locator"],
    } for row in selected]


def render_error_analysis(header: Callable, go_plot: Callable) -> None:
    header("ML Error Analysis", "Saved out-of-fold errors for the 1,016-row Reconstruction, separated by validation design.")
    st.caption("Historical evaluation only · 100 × cooked concentration / raw concentration · Apparent concentration ratio (ACR), not total-mass retention or a live prediction.")
    try:
        with st.spinner("Checking Reconstruction and saved OOF records…"):
            by_design, summaries, dataset_hash = load_reconstruction_errors()
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        st.error(f"ML error analysis unavailable: {exc}")
        return
    st.success("Reconstruction dataset and OOF identity verified; every observation is present once in each design, and saved fold metrics match the predictions.")
    st.caption(f"Dataset: stageA/verified_concentration_ratio_reconstruction/final_verified_master_dataset.csv · SHA-256 {dataset_hash}. Predictions: the same directory's oof_predictions.csv.")
    st.caption("These are the Reconstruction results also listed on Existing ML Results. This page verifies current saved-file identities and metric arithmetic; it does not establish the missing build-time output digest, rerun model training, or independently validate the source measurements.")

    comparison = [{
        "Validation design": DESIGN_LABELS[design], "Observations": value["n"],
        "Pooled OOF R²": round(value["r2"], 4),
        "Mean fold R²": round(sum(error_metrics([row for row in by_design[design] if row["fold"] == fold])["r2"]
                                  for fold in range(1, 6)) / 5, 4),
        "MAE (ACR pp)": round(value["mae"], 2),
        "RMSE (ACR pp)": round(value["rmse"], 2),
        "Median absolute error (ACR pp)": round(value["median_absolute_error"], 2),
        "90th percentile absolute error (ACR pp)": round(value["p90_absolute_error"], 2),
    } for design, value in summaries.items()]
    st.subheader("Performance summary")
    show_dataframe(comparison, hide_index=True, width="stretch")
    st.caption("Pooled OOF R² uses all out-of-fold predictions together. Mean fold R² averages the five fold R² values; the two summaries differ because folds have different target distributions. Both match Existing ML Results for this Reconstruction run.")
    st.caption("R² compares predictions with a mean-prediction baseline; negative means worse on this evaluation. MAE is the average absolute error. RMSE penalizes large misses more strongly. Median absolute error describes a typical miss with less influence from extremes. All errors are ACR percentage points (pp).")
    design = st.radio("Inspect validation design", DESIGNS, format_func=DESIGN_LABELS.get, horizontal=True, key="error_design")
    rows = by_design[design]
    st.info("Molecular grouping holds out molecular identities but allows DOI overlap. DOI holdout keeps each DOI entirely in train or test; DOI is a proxy for source family, not proof of laboratory independence. The negative DOI-held-out R² does not demonstrate reliable unseen-source generalization.")

    st.subheader("Actual versus predicted ACR")
    view = st.radio("Scatter view", ["Zoomed (0–200%)", "Full range"], horizontal=True, key="error_scatter_view")
    fig = go.Figure()
    hover = [[r["observation_id"], r["compound"], r["food_matrix"], r["doi"], r["fold"]] for r in rows]
    fig.add_trace(go.Scattergl(
        x=[r["actual"] for r in rows], y=[r["predicted"] for r in rows], mode="markers",
        name=DESIGN_LABELS[design], marker=dict(color=COLORS[design], size=6, opacity=.58),
        customdata=hover,
        hovertemplate="ID %{customdata[0]}<br>Compound %{customdata[1]}<br>Food %{customdata[2]}<br>DOI %{customdata[3]}<br>Fold %{customdata[4]}<br>Actual %{x:.2f}%<br>Predicted %{y:.2f}%<extra></extra>",
    ))
    extent = max(max(r["actual"] for r in rows), max(r["predicted"] for r in rows))
    fig.add_trace(go.Scatter(x=[0, extent], y=[0, extent], mode="lines", name="Perfect prediction", line=dict(color="#77716A", dash="dash"), hoverinfo="skip"))
    if view.startswith("Zoomed"):
        fig.update_xaxes(range=[0, 200])
        fig.update_yaxes(range=[0, 200])
    fig.update_layout(title=f"{DESIGN_LABELS[design]} OOF predictions", xaxis_title="Actual ACR (%)", yaxis_title="Predicted ACR (%)")
    go_plot(fig)
    st.caption("The zoom changes only the view; metrics and records still use all 1,016 observations.")

    st.subheader("Residual and absolute-error distributions")
    distribution_view = st.radio("Distribution view", ["Central range (±200 pp)", "Full range"],
                                 horizontal=True, key="error_distribution_view")
    left, right = st.columns(2)
    for destination, field, title, axis in ((left, "residual", "Residual: actual − predicted", "Residual (ACR pp)"),
                                             (right, "absolute_error", "Absolute prediction error", "Absolute error (ACR pp)")):
        with destination:
            chart = go.Figure()
            for split in DESIGNS:
                chart.add_trace(go.Histogram(x=[r[field] for r in by_design[split]], name=DESIGN_LABELS[split],
                                             marker_color=COLORS[split], opacity=.63, nbinsx=60))
            chart.update_layout(title=title, barmode="overlay", xaxis_title=axis, yaxis_title="Observations")
            if distribution_view.startswith("Central"):
                chart.update_xaxes(range=[-200, 200] if field == "residual" else [0, 200])
            go_plot(chart, 360)
    st.caption("The central view changes only the axes; both charts and all metrics retain every observation. Extreme ratios stretch the full distribution and contribute strongly to RMSE.")

    st.subheader("Validation comparison and fold performance")
    comparison_fig = go.Figure(go.Bar(x=[DESIGN_LABELS[d] for d in DESIGNS], y=[summaries[d]["r2"] for d in DESIGNS],
                                     marker_color=[COLORS[d] for d in DESIGNS]))
    comparison_fig.add_hline(y=0, line_dash="dash", line_color="#77716A")
    comparison_fig.update_layout(title="Pooled OOF R²", yaxis_title="R² (negative values retained)")
    go_plot(comparison_fig, 300)
    fold_rows = []
    for split in DESIGNS:
        for fold in range(1, 6):
            group = [r for r in by_design[split] if r["fold"] == fold]
            score = error_metrics(group)
            fold_rows.append({"Design": DESIGN_LABELS[split], "Fold": fold, "Test observations": score["n"],
                              "R²": round(score["r2"], 4), "MAE (ACR pp)": round(score["mae"], 2)})
    fold_chart = go.Figure()
    for split in DESIGNS:
        group = [r for r in fold_rows if r["Design"] == DESIGN_LABELS[split]]
        fold_chart.add_trace(go.Bar(x=[str(r["Fold"]) for r in group], y=[r["R²"] for r in group],
                                    name=DESIGN_LABELS[split], marker_color=COLORS[split],
                                    customdata=[[r["Test observations"], r["MAE (ACR pp)"]] for r in group],
                                    hovertemplate="Fold %{x}<br>R² %{y:.3f}<br>Test n %{customdata[0]}<br>MAE %{customdata[1]:.2f} pp<extra></extra>"))
    fold_chart.add_hline(y=0, line_dash="dash", line_color="#77716A")
    fold_chart.update_layout(title="Fold-wise R²", barmode="group", xaxis_title="Fold", yaxis_title="R²")
    go_plot(fold_chart, 350)
    show_dataframe(fold_rows, hide_index=True, width="stretch")

    st.subheader("Descriptive compound and DOI errors")
    st.caption("Group errors summarize these OOF rows; they are not independent group-validation results or causal effects.")
    minimum = st.slider("Minimum observations per group", 2, 50, 10, key="error_group_minimum")
    group_field = st.radio("Group by", ["compound", "doi"], format_func=lambda x: "Compound" if x == "compound" else "DOI / source", horizontal=True, key="error_group_field")
    groups = _error_group_rows(rows, group_field, minimum)
    if not groups:
        st.info("No groups meet the selected observation threshold.")
    else:
        show_dataframe(groups, hide_index=True, width="stretch")
        selected = st.selectbox("Inspect a group’s underlying observations", [r["Group"] for r in groups], key="error_group_selection")
        show_dataframe(_observation_table([r for r in rows if (r[group_field] or "(not recorded)") == selected]), hide_index=True, width="stretch")

    st.subheader("Largest prediction errors")
    worst = sorted(rows, key=lambda row: row["absolute_error"], reverse=True)[:10]
    show_dataframe(_observation_table(worst), hide_index=True, width="stretch")
    chosen = st.selectbox("Inspect an extreme observation", [r["observation_id"] for r in worst], key="error_extreme_selection")
    record = next(r for r in worst if r["observation_id"] == chosen)
    st.write({key: record.get(key, "") for key in ("observation_id", "compound", "food_matrix", "cooking_method", "doi",
                                                   "source_locator", "raw_concentration", "cooked_concentration", "concentration_unit",
                                                   "measurement_basis", "actual", "predicted", "residual", "fold")})
    st.warning("These are historical OOF errors, not live predictions. Extremely high concentration ratios contribute disproportionately to RMSE. The model has not demonstrated reliable generalization to unseen research sources and is not deployment-ready.")


def _safe_source_url(value: str) -> str | None:
    parsed = urlparse(value.strip())
    return value.strip() if parsed.scheme == "https" and parsed.netloc else None


def _stageb_record_detail(row: dict, tables: dict) -> None:
    st.subheader(f"Evidence record {row['Evidence_ID']}")
    compound = tables["compound_by_id"].get(row["Compound_ID"], {})
    study = tables["study_by_id"].get(row["Study_ID"], {})
    publication = tables["bibliography_by_pmid"].get(row["PMID"], {}) if row["PMID"] else {}

    def field(label: str, value: str) -> None:
        st.caption(label)
        st.write(value or "Not recorded")

    left, right = st.columns(2)
    with left:
        field("Compound · registry identity", f"{row['Compound']} · {row['Compound_ID']}")
        field("Drug / probe", row["Drug"])
        field("Evidence type · level", f"{row['Evidence_Type']} · {row['Evidence_Level']}")
    with right:
        field("Study design", row["Study_Design"])
        field("Direction as reported", row["Direction"])
        field("Identity status", row["Identity_Status"])
    st.markdown("**Reported findings and context**")
    field("Reported effect", row["Interaction_Effect"])
    field("Outcome classification", row["Outcome"])
    field("Quantitative outcome as recorded", row["Quantitative_Outcome"])
    field("Preparation and dose", "; ".join(value for value in (row["Preparation"], row["Dose"]) if value))
    field("Population / model", row["Population"])
    field("Study limitations", row["Limitations"])
    with st.expander("Source, identity, and mechanism details"):
        field("Study ID · registry title", f"{row['Study_ID']} · {study.get('Title', '')}")
        field("Publication bibliography title", publication.get("Title", ""))
        field("DOI · PMID", " · ".join(value for value in (row["DOI"], row["PMID"]) if value))
        field("Source locator", row["Source_Locator"])
        field("Source title · authors · year", " · ".join(value for value in (row["Source_Title"], row["Authors"], row["Year"]) if value))
        field("Canonical compound name", compound.get("Canonical_Name", ""))
        field("Mechanism as recorded", row["Mechanism"])
        field("Conflict group", row["Conflict_Group"])
        field("Clinical extrapolation note", row["Clinical_Extrapolation"])
    link = _safe_source_url(row["Source_URL"])
    if link:
        st.link_button("Open recorded publication link", link)
    else:
        st.caption("No verified HTTPS source URL is recorded for this evidence row.")


def _simple_registry(rows: list[dict], title: str, columns: list[str], key: str) -> None:
    st.subheader(title)
    query = st.text_input(f"Search {title.lower()}", key=f"stageb_{key}_search").casefold().strip()
    subset = [row for row in rows if not query or query in " ".join(str(value) for value in row.values()).casefold()]
    st.caption(f"{len(subset):,} of {len(rows):,} records")
    if subset:
        show_dataframe([{field: row.get(field, "") for field in columns} for row in subset], hide_index=True, width="stretch")
    else:
        st.info("No records match this search. Clear or broaden the search term.")


def render_stageb_explorer(header: Callable) -> None:
    header("Stage B – Food–Drug Interaction Evidence Explorer", "Browse the separate, finalized Stage B research-evidence release.")
    st.caption("Release: StageB_FINALIZED · read-only · separate from the older V20 release used by the Stage C local application.")
    try:
        with st.spinner("Checking finalized Stage B tables and source references…"):
            tables = load_stageb_finalized()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.error(f"Stage B finalized evidence unavailable: {exc}")
        return
    st.caption(tables["integrity_note"])
    labels = [("Compounds", "compounds"), ("Evidence records", "evidence"), ("Drug / probe rows", "drugs"),
              ("Bibliography rows", "bibliography"), ("Study rows", "studies"), ("Warnings", "warnings")]
    # Two native metric rows keep the overview readable at narrow widths.
    for trio in (labels[:3], labels[3:]):
        for col, (label, name) in zip(st.columns(3), trio):
            col.metric(label, f"{len(tables[name]):,}")
    st.warning("These records represent curated research evidence, not 317 independently verified clinical interactions. Evidence types, study contexts and source limitations vary. The collection is not an exhaustive or clinically validated interaction database.")

    evidence_tab, compound_tab, drug_tab, study_tab, warning_tab = st.tabs(
        ["Interaction evidence", "Compounds", "Drugs / probes", "Studies & publications", "Warnings"])
    with evidence_tab:
        c1, c2 = st.columns(2)
        query = c1.text_input("Search compound, drug, publication, DOI or record ID", key="stageb_evidence_query").casefold().strip()
        source_query = c2.text_input("Publication / source title", key="stageb_publication_query").casefold().strip()
        c1, c2, c3 = st.columns(3)
        evidence_types = sorted({r["Evidence_Type"] for r in tables["evidence"] if r["Evidence_Type"]})
        study_types = sorted({r["Study_Design"] for r in tables["evidence"] if r["Study_Design"]})
        directions = sorted({r["Direction"] for r in tables["evidence"] if r["Direction"]})
        selected_types = c1.multiselect("Evidence type", evidence_types, key="stageb_evidence_type")
        selected_studies = c2.multiselect("Study design", study_types, key="stageb_study_design")
        selected_directions = c3.multiselect("Direction as recorded", directions, key="stageb_direction")
        filtered = [r for r in tables["evidence"] if
                    (not query or query in " ".join(r.get(k, "") for k in ("Evidence_ID", "Compound", "Drug", "Source_Title", "DOI", "PMID", "Quantitative_Outcome", "Outcome")).casefold())
                    and (not source_query or source_query in " ".join(r.get(k, "") for k in ("Source_Title", "Authors", "DOI", "PMID")).casefold())
                    and (not selected_types or r["Evidence_Type"] in selected_types)
                    and (not selected_studies or r["Study_Design"] in selected_studies)
                    and (not selected_directions or r["Direction"] in selected_directions)]
        st.caption(f"{len(filtered):,} of {len(tables['evidence']):,} evidence records match. Positive, negative, null, conflicting and unclear records remain eligible for display.")
        if not filtered:
            st.info("No evidence records match these filters. Clear or broaden a filter.")
        else:
            page_size = st.selectbox("Rows per page", [10, 20, 50], index=1, key="stageb_page_size")
            pages = math.ceil(len(filtered) / page_size)
            page_number = st.selectbox("Page", list(range(1, pages + 1)), key="stageb_page_number")
            current = filtered[(page_number - 1) * page_size:page_number * page_size]
            summary = [{"Evidence ID": r["Evidence_ID"], "Compound": r["Compound"], "Drug / probe": r["Drug"],
                        "Evidence type": r["Evidence_Type"], "Direction": r["Direction"],
                        "Study": r["Study_ID"], "DOI": r["DOI"]} for r in current]
            selected_id = None
            try:
                event = show_dataframe(summary, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row", key="stageb_evidence_table")
                indices = event.selection.rows
                if indices and indices[0] < len(current):
                    selected_id = current[indices[0]]["Evidence_ID"]
            except TypeError:
                show_dataframe(summary, hide_index=True, width="stretch")
            choice = st.selectbox("Open evidence record", [r["Evidence_ID"] for r in current],
                                  index=next((i for i, r in enumerate(current) if r["Evidence_ID"] == selected_id), 0),
                                  key=f"stageb_detail_{page_number}_{query}_{source_query}")
            record = next(r for r in current if r["Evidence_ID"] == (selected_id or choice))
            _stageb_record_detail(record, tables)
    with compound_tab:
        _simple_registry(tables["compounds"], "Compound registry",
                         ["Compound_ID", "Canonical_Name", "Identity_Status", "Food_Context", "Evidence_Records", "Remaining_Provenance_Gap"], "compounds")
    with drug_tab:
        _simple_registry(tables["drugs"], "Drug / probe registry", ["Drug_ID", "Drug_Probe", "Evidence_Records", "Scope"], "drugs")
    with study_tab:
        _simple_registry(tables["studies"], "Study registry", ["Study_ID", "Title", "PMID", "DOI", "Evidence_Record_Count", "Evidence_Classes", "Verification_Status"], "studies")
        _simple_registry(tables["bibliography"], "Publication bibliography", ["PMID", "Title", "Authors", "Year", "DOI", "DOI_Status"], "bibliography")
    with warning_tab:
        _simple_registry(tables["warnings"], "Warning ledger", ["Warning_ID", "Code", "Description", "Affected", "Final_Disposition", "Remaining_Limitations"], "warnings")

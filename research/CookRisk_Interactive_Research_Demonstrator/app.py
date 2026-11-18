from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from research_data import (
    BATCH021_CURRENT_SHA256,
    BATCH021_HISTORICAL_AUDIT_SHA256,
    DATASET_FAMILIES,
    PROTOTYPE,
    RECONSTRUCTION_REL,
    RECONSTRUCTION_SHA256,
    load_acr_dataset,
    load_dataset_catalog,
    load_selected_metrics,
    load_validation_folds,
    numeric,
)

TITLE = "CookRisk: A Computational Investigation of Cooking-Associated Changes in Bioactive Compound Concentrations Using Machine Learning"

st.set_page_config(page_title="CookRisk Research Demonstrator", page_icon="🧪", layout="wide")
st.markdown(
    """
    <style>
    .block-container {max-width: 1500px; padding-top: 1.4rem; padding-bottom: 3rem;}
    .hero {padding: 1.35rem 1.6rem; border-radius: 14px; background: linear-gradient(110deg,#102a43,#243b53); color: #f0f4f8; margin-bottom: 1rem;}
    .hero h1 {font-size: 1.8rem; margin: 0 0 .45rem 0;}
    .hero p {font-size: 1.02rem; margin: 0; color: #d9e2ec;}
    .status {font-weight: 700; letter-spacing: .025em;}
    </style>
    """,
    unsafe_allow_html=True,
)

PAGES = [
    "Research Overview",
    "Evidence Explorer",
    "ACR Analysis",
    "Cooking & Compound Patterns",
    "Existing ML Results",
    "Validation Lab",
    "Scientific Limitations",
    "Reproducibility & Evidence",
]

with st.sidebar:
    st.title("CookRisk")
    st.caption("Computational research demonstrator")
    page = st.radio("Research modules", PAGES, label_visibility="collapsed")
    st.divider()
    st.warning("Research demonstrator only. No predictions, risk scores, or cooking advice.")
    st.caption("Source data are read-only. Saved metrics are displayed, not recalculated.")


def header(title: str, subtitle: str) -> None:
    st.markdown(f'<section class="hero"><h1>{title}</h1><p>{subtitle}</p></section>', unsafe_allow_html=True)


def acr_rows() -> tuple[list[dict[str, str]] | None, str | None]:
    try:
        rows, digest = load_acr_dataset()
        return rows, digest
    except (OSError, ValueError) as exc:
        st.error(f"Record-level ACR exploration is unavailable: {exc}")
        return None, None


def number_values(rows: list[dict[str, str]], field: str) -> list[float]:
    return [value for row in rows if (value := numeric(row, field)) is not None and math.isfinite(value)]


def filtered_acr_controls(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    st.caption("Filters use the selected file's existing values only. Blank source fields remain visible when no filter is selected.")
    columns = st.columns(4)
    filters = [
        ("Food matrix", "food_matrix"),
        ("Compound", "compound"),
        ("Cooking method", "cooking_method"),
        ("DOI / source", "doi"),
    ]
    selected: dict[str, list[str]] = {}
    for col, (label, field) in zip(columns, filters):
        values = sorted({r.get(field, "").strip() for r in rows if r.get(field, "").strip()})
        if any(not r.get(field, "").strip() for r in rows):
            values.append("(blank / not recorded)")
        selected[field] = col.multiselect(label, values, key=f"filter_{field}")
    result = rows
    for field, choices in selected.items():
        if not choices:
            continue
        keep = set(choices)
        result = [
            r for r in result
            if (r.get(field, "").strip() in keep)
            or (not r.get(field, "").strip() and "(blank / not recorded)" in keep)
        ]
    return result


def source_provenance_card(digest: str, rows_count: int) -> None:
    cols = st.columns(4)
    cols[0].metric("Rows in pinned file", f"{rows_count:,}")
    cols[1].metric("File identity", "SHA-256 verified")
    cols[2].metric("Target", "ACR (%)")
    cols[3].metric("Interpretation", "REPORTED dataset")
    st.code(f"{RECONSTRUCTION_REL.as_posix()}\nSHA-256  {digest}", language="text")
    st.caption("The demonstrator pins the file bytes for stable browsing. This is not owner designation as the canonical ACR dataset and is not new scientific validation.")


def show_rows(rows: list[dict[str, str]], max_height: int = 540) -> None:
    st.dataframe(rows, height=max_height, hide_index=True, use_container_width=True)


def go_plot(fig: go.Figure, height: int = 430) -> None:
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=20, r=20, t=50, b=20), font=dict(family="sans-serif"))
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})


if page == "Research Overview":
    header("Research Overview", "Explore the saved evidence and computational analyses behind CookRisk.")
    st.title(TITLE)
    st.info("This is an academic research demonstrator, not a validated predictor, deployed model, food-safety tool, or cooking-advice system.")
    left, right = st.columns([1.15, .85])
    with left:
        st.subheader("Research question")
        st.write("Can molecular, food-matrix, and cooking-process features characterize reported cooking-associated concentration changes, and do observed patterns transfer to held-out compounds and research sources?")
        st.subheader("Research workflow")
        st.markdown("1. Curate source-linked raw/cooked concentration evidence.\n2. Preserve compound, matrix, method, basis, and source identity.\n3. Compare exploratory ML evaluations under different validation designs.\n4. Examine source transfer, uncertainty, and evidence gaps.")
    with right:
        st.subheader("Target definition")
        st.latex(r"\mathrm{ACR}(\%) = 100 \times \frac{C_{cooked}}{C_{raw}}")
        st.write("ACR is an apparent concentration ratio. It is not total-mass retention. ACR above 100% does not establish increased total analyte mass.")
    st.subheader("Research boundaries")
    cols = st.columns(3)
    cols[0].warning("No causal cooking-method claims")
    cols[1].warning("No bioavailability, exposure, or clinical-risk claims")
    cols[2].warning("No validated model or new-record prediction")
    st.caption("The displayed results are classified as REPORTED, REPRODUCED (only where prior evidence explicitly supports it), PROPOSED, or BLOCKED/UNVERIFIED.")

elif page == "Evidence Explorer":
    header("Evidence Explorer", "Browse one pinned evidence family at a time; other families remain separate.")
    st.subheader("Available research families")
    for item in DATASET_FAMILIES:
        with st.expander(f"{item['family']} — {item['status']}", expanded=item["family"] == "Verified concentration-ratio reconstruction"):
            st.write(f"**Snapshot:** {item['snapshot']}")
            st.write(f"**Target:** {item['target']}")
            st.write(f"**Hash / integrity:** {item['hash']}")
            st.write(f"**Source:** `{item['source']}`")
            st.write(item["interactive"])
    st.divider()
    st.subheader("Record-level exploration: verified concentration-ratio reconstruction")
    st.warning("Selected as a documented evidence package for browsing, not as the canonical ACR dataset. It is distinct from the Batch021 master even though both report 1,016 rows.")
    rows, digest = acr_rows()
    if rows is not None and digest is not None:
        source_provenance_card(digest, len(rows))
        subset = filtered_acr_controls(rows)
        st.write(f"Showing **{len(subset):,}** of **{len(rows):,}** source records. No observations are removed from the source file; filters only change this view.")
        show_rows(subset)
        st.caption("Source locators, raw/cooked concentration strings, units, basis, evidence status, and target values are shown as stored. No unit conversion, imputation, or source-value edit is applied.")

elif page == "ACR Analysis":
    header("ACR Analysis", "Descriptive exploration of the pinned reconstruction's stored target values.")
    st.markdown("**ACR (%) = 100 × cooked concentration / raw concentration.** The analysis below reads the stored target column; it does not derive or convert concentration values.")
    rows, digest = acr_rows()
    if rows is not None:
        source_provenance_card(digest or "", len(rows))
        subset = filtered_acr_controls(rows)
        vals = number_values(subset, "target_value_percent")
        if not vals:
            st.warning("No numeric ACR values are available under the current filters.")
        else:
            mean = statistics.fmean(vals)
            median = statistics.median(vals)
            cols = st.columns(6)
            cols[0].metric("Rows in filtered view", f"{len(subset):,}")
            cols[1].metric("Rows with numeric target", f"{len(vals):,}")
            cols[2].metric("Mean ACR", f"{mean:,.2f}%")
            cols[3].metric("Median ACR", f"{median:,.2f}%")
            cols[4].metric("Minimum / maximum", f"{min(vals):,.2f}% / {max(vals):,.2f}%")
            cols[5].metric("Above 100%", f"{sum(v > 100 for v in vals):,}")
            st.caption(f"Rows with blank or nonnumeric stored target, excluded from numeric plots only: {len(subset) - len(vals)}. They remain present in the evidence table.")
            st.caption("These are interactive descriptive summaries of the filtered stored target values, not a recalculation of historical model metrics. The full reconstruction report's saved summaries remain separately cited in the documentation.")
            hist = go.Figure(go.Histogram(x=vals, nbinsx=40, marker_color="#287d8e"))
            hist.update_layout(title="Stored ACR values (all observations retained)", xaxis_title="ACR (%)", yaxis_title="Observation count")
            go_plot(hist)
            dist = go.Figure()
            for label, mask, color in [
                ("Below 100%", [v for v in vals if v < 100], "#4c78a8"),
                ("Equal to 100%", [v for v in vals if v == 100], "#f2a541"),
                ("Above 100%", [v for v in vals if v > 100], "#d95f59"),
            ]:
                dist.add_trace(go.Bar(name=label, x=[label], y=[len(mask)], marker_color=color))
            dist.update_layout(title="Counts relative to 100%", xaxis_title="Stored ACR category", yaxis_title="Observation count", showlegend=False)
            go_plot(dist, 320)
            box = go.Figure(go.Box(y=vals, name="All filtered observations", boxpoints="outliers", marker_color="#287d8e"))
            box.update_layout(title="Distribution and high-value observations (none removed)", yaxis_title="ACR (%)")
            go_plot(box, 380)
            st.info("ACR above 100% can reflect concentration/basis or analytical context; it does not establish an increase in total analyte mass. Outlying values are retained in every view.")

elif page == "Cooking & Compound Patterns":
    header("Cooking & Compound Patterns", "Descriptive group comparisons; these are not causal effects.")
    st.warning("Observed patterns can reflect source, analytical method, food matrix, preparation, units, moisture basis, or missing protocol metadata. No causal cooking-method claim is supported.")
    rows, digest = acr_rows()
    if rows is not None:
        source_provenance_card(digest or "", len(rows))
        subset = filtered_acr_controls(rows)
        group_field = st.selectbox("Group stored ACR values by", ["cooking_method", "compound", "food_matrix", "doi"], format_func=lambda x: {"cooking_method":"Cooking method", "compound":"Compound", "food_matrix":"Food matrix", "doi":"DOI / source"}[x])
        min_n = st.slider("Minimum observations for a plotted group", 2, 30, 8)
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in subset:
            key = row.get(group_field, "").strip()
            val = numeric(row, "target_value_percent")
            if key and val is not None and math.isfinite(val):
                grouped[key].append(val)
        eligible = [(key, vals) for key, vals in grouped.items() if len(vals) >= min_n]
        eligible.sort(key=lambda item: (-len(item[1]), item[0]))
        plotted_groups = eligible[:20]
        numeric_group_rows = sum(len(v) for v in grouped.values())
        plotted_rows = sum(len(v) for _, v in plotted_groups)
        st.caption(f"Filtered rows: {len(subset)}; rows with numeric target and recorded group: {numeric_group_rows}; rows represented in the chart's eligible top 20 groups: {plotted_rows}. The remaining rows are unplotted because of missing fields, the minimum-support threshold, or the top-20 display cap; source records remain unchanged.")
        if len(eligible) < 2:
            st.info(f"Fewer than two groups meet the minimum support of {min_n} observations. Lower the support threshold or broaden filters; no comparison is fabricated.")
        else:
            fig = go.Figure()
            for key, vals in plotted_groups:
                fig.add_trace(go.Box(y=vals, name=f"{key} (n={len(vals)})", boxpoints=False))
            fig.update_layout(title=f"Stored ACR distribution by {group_field.replace('_', ' ')} (groups with n ≥ {min_n})", yaxis_title="ACR (%)", xaxis_title="Documented group")
            go_plot(fig, max(430, 30 * min(len(plotted_groups), 18)))
            table = [{"group": key, "n": len(v), "median_acr_percent": statistics.median(v), "mean_acr_percent": statistics.fmean(v)} for key, v in plotted_groups]
            st.caption("Group summaries are calculated descriptively from stored ACR target values. They are not adjusted for source or protocol and must not be interpreted causally.")
            st.dataframe(table, hide_index=True, use_container_width=True)

elif page == "Existing ML Results":
    header("Existing ML Results", "Compare saved evaluations while keeping datasets, targets, and validation designs separate.")
    st.info("All values below are saved reported metrics. The demonstrator does not train models, load fitted models, infer predictions, or recalculate these metrics.")
    try:
        metrics = load_selected_metrics()
        family_options = sorted({r["result_family"] for r in metrics})
        families = st.multiselect("Result family", family_options, default=family_options)
        target_options = sorted({r["target"] for r in metrics if r["result_family"] in families})
        targets = st.multiselect("Target", target_options, default=target_options)
        designs = sorted({r["validation"] for r in metrics if r["result_family"] in families and r["target"] in targets})
        selected_designs = st.multiselect("Evaluation design", designs, default=designs)
        filtered = [r for r in metrics if r["result_family"] in families and r["target"] in targets and r["validation"] in selected_designs]
        st.dataframe(filtered, hide_index=True, use_container_width=True)
        numeric_rows = [r for r in filtered if numeric(r, "r2") is not None]
        if numeric_rows and len(families) == 1 and len(targets) == 1:
            metric_choice = st.selectbox("Plot saved metric", ["r2", "mae", "rmse"], format_func=lambda x: {"r2":"R² (dimensionless)", "mae":"MAE (recorded target scale)", "rmse":"RMSE (recorded target scale)"}[x])
            fig = go.Figure(go.Bar(x=[f"{r['model']} · {r['validation']}" for r in numeric_rows], y=[numeric(r, metric_choice) for r in numeric_rows], marker_color=["#c84c4c" if (metric_choice == "r2" and (numeric(r, metric_choice) or 0) < 0) else "#287d8e" for r in numeric_rows]))
            y_label = "R² (dimensionless)" if metric_choice == "r2" else ("ACR percentage points" if targets[0] == "ACR" else "Unresolved historical Retention_Final scale")
            fig.update_layout(title=f"Saved {metric_choice.upper()} · {families[0]} · {targets[0]}", xaxis_title="Model and evaluation design", yaxis_title=y_label)
            go_plot(fig, max(450, len(numeric_rows) * 22))
        elif numeric_rows:
            st.info("Select exactly one result family and one target to plot saved metrics. This prevents charts from combining different dataset snapshots or target scales; the table above can still be used to inspect separate reported rows.")
        st.caption("MAE/RMSE units are those recorded for each target. For ACR they are ACR percentage points; for historical Retention_Final the scale/unit semantics remain unresolved. See local reference: `research/CookRisk_Computational_Research_Prototype/tables/EXISTING_METRICS_SELECTED.csv`.")
    except (OSError, KeyError) as exc:
        st.error(f"Saved metric catalog unavailable or malformed: {exc}")

elif page == "Validation Lab":
    header("Validation Lab", "Compare validation questions and inspect saved fold-level results.")
    st.markdown("**Random split** can place related rows or sources on both sides. **Molecular-grouped** evaluation holds molecular identities out but can retain DOI overlap. **DOI/source-held-out** evaluation holds DOI groups out; DOI is only a proxy for independent research sources and does not guarantee laboratory independence.")
    st.error(f"BATCH021 AUDIT: REPORTED HISTORICAL RESULT — CURRENT SNAPSHOT ATTRIBUTION BLOCKED/UNVERIFIED.\n\nHistorical audit input SHA-256: `{BATCH021_HISTORICAL_AUDIT_SHA256}`\n\nCurrent Batch021 CSV SHA-256: `{BATCH021_CURRENT_SHA256}`")
    st.write("The saved pooled ExtraTrees R² values are −0.067833 (molecular grouped) and −0.065645 (DOI-held-out). These are reported historical outputs, not verified against the currently available Batch021 CSV.")
    st.subheader("Pooled versus fold-wise R²")
    st.caption("The following saved figure data are fold-wise values. One molecular-grouped fold is positive. Pooled scores above summarize all out-of-fold predictions and are a different calculation; they are both negative.")
    try:
        folds = load_validation_folds()
        fig = go.Figure()
        colors = {"molecular_grouped":"#287d8e", "source_held_out":"#d17a22"}
        labels = {"molecular_grouped":"Molecular-grouped (fold-wise)", "source_held_out":"DOI/source-held-out (fold-wise)"}
        for strategy in ("molecular_grouped", "source_held_out"):
            group = [r for r in folds if r.get("validation_strategy") == strategy]
            fig.add_trace(go.Scatter(x=[int(r["fold"]) for r in group], y=[float(r["r2"]) for r in group], mode="lines+markers", name=labels[strategy], line=dict(color=colors[strategy], width=3), marker=dict(size=9)))
        fig.add_hline(y=0, line_dash="dash", line_color="#666")
        fig.update_layout(title="Saved fold-wise R² — historical audit input; current attribution blocked", xaxis_title="Fold", yaxis_title="Fold R²")
        go_plot(fig)
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Saved fold metrics unavailable or malformed: {exc}")
    st.caption("Local source: `stageA/molecular_vs_source_validation_audit/fold_metrics.csv`; pooled values: `stageA/molecular_vs_source_validation_audit/validation_summary.json`. Both are reported historical evidence; the exact input bytes remain unavailable.")

elif page == "Scientific Limitations":
    header("Scientific Limitations", "Limitations are part of the evidence, not hidden behind a general disclaimer.")
    limitations = [
        ("Batch021 audit input hash mismatch", f"Historical audit input `{BATCH021_HISTORICAL_AUDIT_SHA256}` differs from current Batch021 CSV `{BATCH021_CURRENT_SHA256}`. Exact historical bytes have not been recovered; current-snapshot attribution is BLOCKED/UNVERIFIED."),
        ("Separate dataset families", "The 1,124-row Retention_Final benchmark, 439-row ACR prototype, Batch021 master, verified reconstruction, 338-row strict subset, and other recovery snapshots have different targets, inclusion rules, hashes, or provenance. Equal row counts do not make them identical."),
        ("No canonical ACR snapshot", "No owner-designated canonical ACR dataset is established in the reviewed evidence."),
        ("Historical target semantics", "Retention_Final remains separate from ACR, and its original equation/unit semantics are unresolved."),
        ("Source-held-out performance", "Several reported source-held-out evaluations have negative R². They do not demonstrate robust source transfer."),
        ("Source independence", "DOI grouping is a source-family proxy and does not guarantee independence of laboratory, protocol, or researchers."),
        ("Missing protocol metadata", "Temperature, duration, basis, assay, and other cooking/measurement context are incomplete across records."),
        ("Extreme observations", "High ACR values influence RMSE and R²; values are retained and require contextual interpretation rather than silent deletion."),
        ("ACR is not total-mass retention", "ACR above 100% does not establish increased total analyte mass; compatible mass/yield and basis data would be needed."),
        ("No validated predictor", "No validated deployment model, new-record inference capability, clinical risk estimate, nutrition/exposure estimate, or cooking recommendation is provided."),
        ("Reproducibility scope", "Prior repeated-run evidence applies to the specific 1,124-row benchmark only. Historical predictions differ, and ACR packages were not freshly reproduced here."),
    ]
    for title, text in limitations:
        with st.expander(title, expanded=title == "Batch021 audit input hash mismatch"):
            st.write(text)

elif page == "Reproducibility & Evidence":
    header("Reproducibility & Evidence", "Inspect snapshot identity, result status, and the limits of the available provenance.")
    st.subheader("Evidence status definitions")
    st.markdown("- **REPRODUCED:** only where prior repository evidence documents independent reproduction of that specific result.\n- **REPORTED:** present in saved source reports, tables, plots, or outputs; not freshly rerun here.\n- **PROPOSED:** future research, not an existing result.\n- **BLOCKED/UNVERIFIED:** a provenance, hash, authorization, or evidence gap prevents verification.")
    st.subheader("Dataset family register")
    st.dataframe(DATASET_FAMILIES, hide_index=True, use_container_width=True)
    st.subheader("Documented dataset snapshots")
    try:
        st.dataframe(load_dataset_catalog(), hide_index=True, use_container_width=True)
    except (OSError, KeyError) as exc:
        st.warning(f"Snapshot catalog unavailable: {exc}")
    st.subheader("Key provenance limitation")
    st.code(f"Batch021 historical audit input: {BATCH021_HISTORICAL_AUDIT_SHA256}\nCurrent Batch021 CSV:          {BATCH021_CURRENT_SHA256}\nSelected reconstruction:       {RECONSTRUCTION_SHA256}", language="text")
    st.info("The selected reconstruction hash identifies the current file bytes for this demonstrator. Its 1,016 rows do not make it identical to Batch021, and this hash does not designate it as canonical.")
    st.subheader("Local source references")
    for path in [
        "research/CookRisk_Computational_Research_Prototype/01_RESEARCH_OVERVIEW.md",
        "research/CookRisk_Computational_Research_Prototype/06_VALIDATION_AND_GENERALIZATION.md",
        "research/CookRisk_Computational_Research_Prototype/UPDATED_RESEARCH_READINESS_ASSESSMENT.md",
        "stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md",
        "stageA/molecular_vs_source_validation_audit/validation_summary.json",
        "stageA/final_prototype_2026_11_10/manifest.json",
    ]:
        st.code(path, language="text")
    st.caption("Open these paths in the local repository to inspect the underlying records. No Stage B or restricted Stage C/D content is read by this demonstrator.")

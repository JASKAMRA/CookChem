from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / 'data' / 'preprocessing' / 'final' / 'cookchem_molecular_retention_preprocessed.csv'
EDA_DIR = ROOT / 'eda'
SCRIPT_DIR = EDA_DIR / 'scripts'
OUTPUT_DIR = EDA_DIR / 'outputs'
FIGURES_DIR = OUTPUT_DIR / 'figures'
TABLES_DIR = OUTPUT_DIR / 'tables'
SUMMARIES_DIR = OUTPUT_DIR / 'summaries'
REPORT_DIR = EDA_DIR / 'reports'
REPORT_PATH = REPORT_DIR / 'eda_report.md'
TARGET = 'Retention_Final'
APPARENT = 'Apparent_Increase'
COMPOUND_ID = 'Canonical_Molecular_ID'
COMPOUND_NAME = 'Canonical_Compound_Name'
FOOD = 'Food_Name_Standardized'
METHOD = 'Cooking_Method_Standardized'
MEDIUM = 'Cooking_Medium_Standardized'
ASSAY = 'Assay_Method_Standardized'
CLASS = 'Compound_Class_Standardized'
OIL = 'Oil_Type_Standardized'
UNIT = 'Initial_Unit_Standardized'
KEY_MISSINGNESS_COLUMNS = ['Pressure_kPa', 'Microwave_Power_W', 'Oil_Type_Standardized', 'Food_Water_Ratio']
DESCRIPTORS = [
    'RDKit_Molecular_Weight',
    'RDKit_LogP',
    'RDKit_TPSA',
    'RDKit_HBond_Donors',
    'RDKit_HBond_Acceptors',
    'RDKit_Rotatable_Bonds',
    'RDKit_Aromatic_Rings',
    'RDKit_Hydroxyl_Groups',
    'RDKit_Heavy_Atom_Count',
]
CATEGORICAL_FEATURES = [
    CLASS,
    METHOD,
    MEDIUM,
    FOOD,
    ASSAY,
    OIL,
    UNIT,
]
IDENTIFIER_COLUMNS = [
    'Record_ID', 'Paper_ID', 'DOI', 'DOI_Normalized', 'Source_Paper_Key',
    'Canonical_Molecular_ID', 'Compound_Name', 'Canonical_Compound_Name',
    'Compound_Class', 'Food_Name', 'Cooking_Method', 'Authors', 'Journal',
    'Country', 'Scientific_Name', 'Plant_Part', 'Canonical_SMILES'
]
NUMERIC_CORRELATION_FEATURES = [
    'Year', 'Temperature_C', 'Cooking_Time_min', 'Pressure_kPa', 'Microwave_Power_W',
    'Sample_Weight_g', 'Initial_Concentration', 'Replicates_n', *DESCRIPTORS
]
FONT_CANDIDATES = ['arial.ttf', 'calibri.ttf', 'segoeui.ttf', 'tahoma.ttf']
SEED = 42


def ensure_dirs() -> None:
    for path in [SCRIPT_DIR, FIGURES_DIR, TABLES_DIR, SUMMARIES_DIR, REPORT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_font(size: int) -> ImageFont.ImageFont:
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int = 16, fill: str = '#111111') -> None:
    draw.text(xy, text, font=load_font(size), fill=fill)


def shorten(text: object, width: int = 18) -> str:
    if pd.isna(text):
        return 'Missing'
    s = str(text)
    return s if len(s) <= width else s[: width - 1] + '...'


def save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def series_stats(series: pd.Series, percentiles: list[float]) -> dict[str, float | int | None]:
    numeric = pd.to_numeric(series, errors='coerce').dropna()
    if numeric.empty:
        return {'count': 0}
    stats = {
        'count': int(numeric.count()),
        'mean': float(numeric.mean()),
        'median': float(numeric.median()),
        'std': float(numeric.std(ddof=1)) if len(numeric) > 1 else 0.0,
        'min': float(numeric.min()),
        'max': float(numeric.max()),
        'skewness': float(numeric.skew()) if len(numeric) > 2 else 0.0,
        'kurtosis': float(numeric.kurt()) if len(numeric) > 3 else 0.0,
    }
    for p in percentiles:
        stats[f'P{int(p * 100)}'] = float(numeric.quantile(p))
    return stats


def fisher_p_value(r: float, n: int) -> float | None:
    if n < 4 or pd.isna(r):
        return None
    if abs(r) >= 1:
        return 0.0
    z = math.atanh(max(min(r, 0.999999), -0.999999)) * math.sqrt(max(n - 3, 1))
    return float(math.erfc(abs(z) / math.sqrt(2)))


def correlation_with_p(x: pd.Series, y: pd.Series, method: str) -> tuple[float | None, float | None, int]:
    pair = pd.concat([pd.to_numeric(x, errors='coerce'), pd.to_numeric(y, errors='coerce')], axis=1).dropna()
    n = int(len(pair))
    if n < 3:
        return None, None, n
    a = pair.iloc[:, 0]
    b = pair.iloc[:, 1]
    if method == 'spearman':
        a = a.rank(method='average')
        b = b.rank(method='average')
    r = float(a.corr(b, method='pearson'))
    return r, fisher_p_value(r, n), n


def markdown_table(df: pd.DataFrame, limit: int | None = None) -> str:
    if limit is not None:
        df = df.head(limit)
    if df.empty:
        return '_No rows._'
    printable = df.fillna('').astype(str)
    cols = printable.columns.tolist()
    lines = ['| ' + ' | '.join(cols) + ' |', '| ' + ' | '.join(['---'] * len(cols)) + ' |']
    for _, row in printable.iterrows():
        lines.append('| ' + ' | '.join(row[c] for c in cols) + ' |')
    return '\n'.join(lines)


def base_canvas(title: str, width: int = 1200, height: int = 800) -> tuple[Image.Image, ImageDraw.ImageDraw, dict[str, int]]:
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    margins = {'left': 120, 'right': 40, 'top': 90, 'bottom': 90}
    draw.rectangle((0, 0, width, height), fill='white')
    draw_text(draw, (40, 25), title, 28)
    draw.line((margins['left'], height - margins['bottom'], width - margins['right'], height - margins['bottom']), fill='#333333', width=2)
    draw.line((margins['left'], margins['top'], margins['left'], height - margins['bottom']), fill='#333333', width=2)
    return image, draw, margins


def value_to_y(value: float, vmin: float, vmax: float, top: int, bottom: int) -> int:
    if vmax == vmin:
        return (top + bottom) // 2
    ratio = (value - vmin) / (vmax - vmin)
    return int(bottom - ratio * (bottom - top))


def draw_histogram(series: pd.Series, path: Path, title: str, bins: int = 20, log_transform: bool = False) -> None:
    numeric = pd.to_numeric(series, errors='coerce').dropna()
    if log_transform:
        numeric = numeric[numeric > 0]
        numeric = np.log10(numeric)
    image, draw, margins = base_canvas(title)
    if numeric.empty:
        draw_text(draw, (140, 160), 'No data available', 20)
        image.save(path)
        return
    counts, edges = np.histogram(numeric.to_numpy(), bins=min(bins, max(5, int(np.sqrt(len(numeric))))))
    top = margins['top'] + 20
    bottom = image.height - margins['bottom']
    left = margins['left'] + 10
    right = image.width - margins['right']
    plot_w = right - left
    plot_h = bottom - top
    max_count = max(int(counts.max()), 1)
    bar_w = plot_w / len(counts)
    for idx, count in enumerate(counts):
        x0 = left + idx * bar_w + 4
        x1 = left + (idx + 1) * bar_w - 4
        y1 = bottom
        y0 = bottom - (count / max_count) * plot_h
        draw.rectangle((x0, y0, x1, y1), fill='#4c956c', outline='#2c6e49')
    draw_text(draw, (left, bottom + 20), f'min={numeric.min():.2f}', 14)
    draw_text(draw, (right - 180, bottom + 20), f'max={numeric.max():.2f}', 14)
    draw_text(draw, (left, top - 30), f'n={len(numeric)} bins={len(counts)}', 14)
    image.save(path)


def draw_boxplot(series: pd.Series, path: Path, title: str) -> None:
    numeric = pd.to_numeric(series, errors='coerce').dropna()
    image, draw, margins = base_canvas(title)
    if numeric.empty:
        draw_text(draw, (140, 160), 'No data available', 20)
        image.save(path)
        return
    q1, med, q3 = numeric.quantile([0.25, 0.5, 0.75]).tolist()
    iqr = q3 - q1
    lower = max(float(numeric.min()), q1 - 1.5 * iqr)
    upper = min(float(numeric.max()), q3 + 1.5 * iqr)
    top = margins['top'] + 40
    bottom = image.height - margins['bottom']
    center = (margins['left'] + image.width - margins['right']) // 2
    y_q1 = value_to_y(q1, float(numeric.min()), float(numeric.max()), top, bottom)
    y_med = value_to_y(med, float(numeric.min()), float(numeric.max()), top, bottom)
    y_q3 = value_to_y(q3, float(numeric.min()), float(numeric.max()), top, bottom)
    y_low = value_to_y(lower, float(numeric.min()), float(numeric.max()), top, bottom)
    y_up = value_to_y(upper, float(numeric.min()), float(numeric.max()), top, bottom)
    draw.line((center, y_low, center, y_up), fill='#333333', width=3)
    draw.rectangle((center - 100, y_q3, center + 100, y_q1), outline='#8b1e3f', fill='#f9d6e5', width=3)
    draw.line((center - 100, y_med, center + 100, y_med), fill='#8b1e3f', width=3)
    draw.line((center - 50, y_low, center + 50, y_low), fill='#333333', width=3)
    draw.line((center - 50, y_up, center + 50, y_up), fill='#333333', width=3)
    draw_text(draw, (150, top), f'min={numeric.min():.2f} q1={q1:.2f} median={med:.2f} q3={q3:.2f} max={numeric.max():.2f}', 16)
    image.save(path)


def draw_barh(labels: list[str], values: list[float], path: Path, title: str, color: str = '#3d5a80') -> None:
    image, draw, margins = base_canvas(title, height=max(600, 120 + 28 * max(1, len(labels))))
    left = margins['left'] + 180
    right = image.width - margins['right'] - 20
    top = margins['top'] + 20
    bottom = image.height - margins['bottom']
    max_val = max(values) if values else 1
    row_h = max((bottom - top) / max(len(labels), 1), 24)
    for idx, (label, value) in enumerate(zip(labels, values)):
        y0 = top + idx * row_h + 4
        y1 = y0 + row_h - 10
        x0 = left
        x1 = left + ((value / max_val) * (right - left))
        draw.rectangle((x0, y0, x1, y1), fill=color, outline='#1d3557')
        draw_text(draw, (30, int(y0)), shorten(label, 26), 15)
        draw_text(draw, (int(x1) + 8, int(y0)), f'{value:.2f}' if isinstance(value, float) and not float(value).is_integer() else f'{int(value)}', 15)
    image.save(path)


def draw_scatter(x: pd.Series, y: pd.Series, path: Path, title: str, x_label: str, y_label: str) -> None:
    pair = pd.concat([pd.to_numeric(x, errors='coerce'), pd.to_numeric(y, errors='coerce')], axis=1).dropna()
    image, draw, margins = base_canvas(title)
    if pair.empty:
        draw_text(draw, (140, 160), 'No data available', 20)
        image.save(path)
        return
    left = margins['left'] + 20
    right = image.width - margins['right']
    top = margins['top'] + 20
    bottom = image.height - margins['bottom']
    x_min, x_max = float(pair.iloc[:, 0].min()), float(pair.iloc[:, 0].max())
    y_min, y_max = float(pair.iloc[:, 1].min()), float(pair.iloc[:, 1].max())
    for xv, yv in pair.itertuples(index=False):
        px = left if x_max == x_min else left + ((xv - x_min) / (x_max - x_min)) * (right - left)
        py = value_to_y(float(yv), y_min, y_max, top, bottom)
        draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill='#1d3557')
    draw_text(draw, (left, bottom + 20), f'{x_label}: {x_min:.2f} to {x_max:.2f}', 14)
    draw_text(draw, (left, top - 30), f'{y_label}: {y_min:.2f} to {y_max:.2f}; n={len(pair)}', 14)
    image.save(path)


def draw_heatmap(matrix: pd.DataFrame, path: Path, title: str) -> None:
    image, draw, margins = base_canvas(title, width=1200, height=900)
    if matrix.empty:
        draw_text(draw, (140, 160), 'No data available', 20)
        image.save(path)
        return
    labels = list(matrix.columns)
    n = len(labels)
    left = margins['left'] + 160
    top = margins['top'] + 40
    size = min(50, int((image.width - left - margins['right'] - 20) / max(n, 1)))
    for i, row_label in enumerate(labels):
        draw_text(draw, (40, top + i * size + 12), shorten(row_label, 18), 14)
        draw_text(draw, (left + i * size, top - 28), shorten(row_label, 10), 12)
        for j, col_label in enumerate(labels):
            val = float(matrix.iloc[i, j]) if pd.notna(matrix.iloc[i, j]) else 0.0
            intensity = int(255 * (1 - min(abs(val), 1.0)))
            color = (intensity, 220, 255) if val >= 0 else (255, intensity, intensity)
            x0 = left + j * size
            y0 = top + i * size
            draw.rectangle((x0, y0, x0 + size, y0 + size), fill=color, outline='#cccccc')
            draw_text(draw, (x0 + 5, y0 + 16), f'{val:.2f}', 12)
    image.save(path)


def draw_group_boxplots(groups: list[tuple[str, pd.Series]], path: Path, title: str) -> None:
    groups = [(label, pd.to_numeric(series, errors='coerce').dropna()) for label, series in groups]
    groups = [(label, series) for label, series in groups if not series.empty]
    image, draw, margins = base_canvas(title, width=1400, height=850)
    if not groups:
        draw_text(draw, (140, 160), 'No data available', 20)
        image.save(path)
        return
    all_values = pd.concat([series for _, series in groups], ignore_index=True)
    vmin, vmax = float(all_values.min()), float(all_values.max())
    left = margins['left'] + 30
    right = image.width - margins['right']
    top = margins['top'] + 30
    bottom = image.height - margins['bottom'] - 80
    step = (right - left) / max(len(groups), 1)
    for idx, (label, series) in enumerate(groups):
        center = left + idx * step + step / 2
        q1, med, q3 = series.quantile([0.25, 0.5, 0.75]).tolist()
        iqr = q3 - q1
        lower = max(float(series.min()), q1 - 1.5 * iqr)
        upper = min(float(series.max()), q3 + 1.5 * iqr)
        y_q1 = value_to_y(q1, vmin, vmax, top, bottom)
        y_med = value_to_y(med, vmin, vmax, top, bottom)
        y_q3 = value_to_y(q3, vmin, vmax, top, bottom)
        y_low = value_to_y(lower, vmin, vmax, top, bottom)
        y_up = value_to_y(upper, vmin, vmax, top, bottom)
        draw.line((center, y_low, center, y_up), fill='#333333', width=2)
        draw.rectangle((center - 18, y_q3, center + 18, y_q1), outline='#6d597a', fill='#cdb4db', width=2)
        draw.line((center - 18, y_med, center + 18, y_med), fill='#6d597a', width=2)
        draw_text(draw, (int(center - 28), bottom + 12), shorten(label, 10), 12)
    image.save(path)


def draw_missingness_group_comparison(summary: pd.DataFrame, path: Path, title: str) -> None:
    image, draw, margins = base_canvas(title, width=1400, height=900)
    if summary.empty:
        draw_text(draw, (140, 160), 'No data available', 20)
        image.save(path)
        return
    vars_ = summary['variable'].drop_duplicates().tolist()
    left = margins['left'] + 40
    top = margins['top'] + 20
    row_h = 160
    for idx, variable in enumerate(vars_):
        sub = summary[summary['variable'] == variable].reset_index(drop=True)
        y_base = top + idx * row_h
        draw_text(draw, (40, y_base + 30), variable, 18)
        for jdx, row in sub.iterrows():
            x0 = left + jdx * 260
            width = 180
            mean = float(row['mean_retention']) if pd.notna(row['mean_retention']) else 0.0
            pct = float(row['group_percent']) if pd.notna(row['group_percent']) else 0.0
            bar_h = max(4, int((mean / max(float(summary['mean_retention'].max()), 1.0)) * 70))
            draw.rectangle((x0, y_base + 90 - bar_h, x0 + width, y_base + 90), fill='#457b9d')
            draw_text(draw, (x0, y_base + 100), row['group'], 14)
            draw_text(draw, (x0, y_base + 120), f"n={int(row['count'])} ({pct:.1f}%)", 13)
            draw_text(draw, (x0, y_base + 138), f"mean={mean:.1f} med={float(row['median_retention']):.1f}", 13)
    image.save(path)

def overview_outputs(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols]
    overview = {
        'input_path': str(INPUT_PATH.relative_to(ROOT)),
        'observations': int(len(df)),
        'columns': int(len(df.columns)),
        'unique_compounds': int(df[COMPOUND_ID].nunique(dropna=True)),
        'unique_foods': int(df[FOOD].nunique(dropna=True)),
        'unique_cooking_methods': int(df[METHOD].nunique(dropna=True)),
        'unique_cooking_media': int(df[MEDIUM].nunique(dropna=True)),
        'unique_assay_methods': int(df[ASSAY].nunique(dropna=True)),
        'target_column': TARGET,
        'numerical_feature_count': int(len(numeric_cols)),
        'categorical_feature_count': int(len(categorical_cols)),
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    }
    pd.DataFrame([overview]).to_csv(TABLES_DIR / 'dataset_overview.csv', index=False)
    save_json(SUMMARIES_DIR / 'dataset_overview.json', overview)
    return overview


def missingness_outputs(df: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame({
        'column': df.columns,
        'dtype': [str(t) for t in df.dtypes],
        'non_null_values': df.notna().sum().values,
        'missing_values': df.isna().sum().values,
        'missing_percentage': (df.isna().mean().values * 100).round(4),
        'unique_values': [int(df[c].nunique(dropna=True)) for c in df.columns],
    }).sort_values(['missing_percentage', 'column'], ascending=[False, True]).reset_index(drop=True)
    summary.to_csv(TABLES_DIR / 'missingness_summary.csv', index=False)
    top = summary.copy()
    top['label'] = top['column'] + ' (' + top['missing_percentage'].round(1).astype(str) + '%)'
    draw_barh(top.head(20)['column'].tolist()[::-1], top.head(20)['missing_percentage'].tolist()[::-1], FIGURES_DIR / 'missingness_overview.png', 'Top Missingness by Column', color='#e76f51')
    return summary


def retention_outputs(df: pd.DataFrame) -> dict:
    stats = series_stats(df[TARGET], [0.01, 0.05, 0.10, 0.25, 0.75, 0.90, 0.95, 0.99])
    pd.DataFrame([stats]).to_csv(TABLES_DIR / 'retention_summary.csv', index=False)
    draw_histogram(df[TARGET], FIGURES_DIR / 'retention_distribution.png', 'Retention Distribution')
    draw_boxplot(df[TARGET], FIGURES_DIR / 'retention_boxplot.png', 'Retention Boxplot')
    draw_histogram(df[TARGET], FIGURES_DIR / 'retention_log_visualization.png', 'Log10 Retention Visualization', log_transform=True)
    return stats


def apparent_increase_outputs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for flag, group in df.groupby(APPARENT, dropna=False):
        label = 'Retention > 100' if int(flag) == 1 else 'Retention <= 100'
        rows.append({
            'group': label,
            'apparent_increase': int(flag),
            'count': int(len(group)),
            'percentage': float(len(group) / len(df) * 100),
            'mean_retention': float(group[TARGET].mean()),
            'median_retention': float(group[TARGET].median()),
            'min_retention': float(group[TARGET].min()),
            'max_retention': float(group[TARGET].max()),
        })
    out = pd.DataFrame(rows).sort_values('apparent_increase').reset_index(drop=True)
    out.to_csv(TABLES_DIR / 'apparent_increase_summary.csv', index=False)
    groups = [(row['group'], df.loc[df[APPARENT] == row['apparent_increase'], TARGET]) for _, row in out.iterrows()]
    draw_group_boxplots(groups, FIGURES_DIR / 'apparent_increase_comparison.png', 'Retention by Apparent Increase Group')
    return out


def top_retention_outputs(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['Record_ID', 'Compound_Name', COMPOUND_ID, 'Food_Name', METHOD, 'Temperature_C', 'Cooking_Time_min', TARGET, APPARENT]
    top = df[cols].sort_values(TARGET, ascending=False).head(20).reset_index(drop=True)
    top.to_csv(TABLES_DIR / 'top_retention_observations.csv', index=False)
    return top


def compound_frequency_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    freq = df.groupby(COMPOUND_ID, dropna=False).agg(
        Canonical_Compound_Name=(COMPOUND_NAME, lambda s: s.dropna().iloc[0] if not s.dropna().empty else 'Missing'),
        observation_count=(COMPOUND_ID, 'size')
    ).reset_index().sort_values(['observation_count', 'Canonical_Compound_Name'], ascending=[False, True]).reset_index(drop=True)
    freq.to_csv(TABLES_DIR / 'compound_frequency_eda.csv', index=False)
    counts = freq['observation_count']
    stats = {
        'min_observations_per_compound': int(counts.min()),
        'max_observations_per_compound': int(counts.max()),
        'mean_observations_per_compound': float(counts.mean()),
        'median_observations_per_compound': float(counts.median()),
        'P10': float(counts.quantile(0.10)),
        'P25': float(counts.quantile(0.25)),
        'P75': float(counts.quantile(0.75)),
        'P90': float(counts.quantile(0.90)),
        'P95': float(counts.quantile(0.95)),
        'compounds_with_1_observation': int((counts == 1).sum()),
        'compounds_with_le_2_observations': int((counts <= 2).sum()),
        'compounds_with_le_5_observations': int((counts <= 5).sum()),
        'compounds_with_ge_10_observations': int((counts >= 10).sum()),
        'compounds_with_ge_20_observations': int((counts >= 20).sum()),
    }
    draw_histogram(counts, FIGURES_DIR / 'compound_frequency_distribution.png', 'Compound Observation Frequency', bins=20)
    top20 = freq.head(20).copy()
    top20.to_csv(TABLES_DIR / 'top_compounds_by_observations.csv', index=False)
    draw_barh(top20[COMPOUND_NAME].tolist()[::-1], top20['observation_count'].tolist()[::-1], FIGURES_DIR / 'top_compounds_by_observations.png', 'Top 20 Compounds by Observation Count', color='#2a9d8f')
    return freq, stats, top20


def compound_retention_outputs(df: pd.DataFrame, top_compounds: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(COMPOUND_ID, dropna=False).agg(
        Canonical_Compound_Name=(COMPOUND_NAME, lambda s: s.dropna().iloc[0] if not s.dropna().empty else 'Missing'),
        n=(TARGET, 'size'),
        mean_retention=(TARGET, 'mean'),
        median_retention=(TARGET, 'median'),
        std_retention=(TARGET, 'std'),
        min_retention=(TARGET, 'min'),
        max_retention=(TARGET, 'max')
    ).reset_index()
    summary.to_csv(TABLES_DIR / 'compound_retention_summary.csv', index=False)
    top_ids = top_compounds[COMPOUND_ID].head(12).tolist()
    groups = []
    for compound_id in top_ids:
        label = df.loc[df[COMPOUND_ID] == compound_id, COMPOUND_NAME].iloc[0]
        groups.append((label, df.loc[df[COMPOUND_ID] == compound_id, TARGET]))
    draw_group_boxplots(groups, FIGURES_DIR / 'retention_by_top_compounds.png', 'Retention Distributions for Top Compounds')
    return summary


def class_outputs(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(CLASS, dropna=False).agg(
        observation_count=(TARGET, 'size'),
        unique_compounds=(COMPOUND_ID, 'nunique'),
        mean_retention=(TARGET, 'mean'),
        median_retention=(TARGET, 'median'),
        std_retention=(TARGET, 'std'),
    ).reset_index().sort_values('observation_count', ascending=False).reset_index(drop=True)
    summary.to_csv(TABLES_DIR / 'compound_class_summary.csv', index=False)
    plot_df = summary.head(15)
    draw_barh(plot_df[CLASS].fillna('Missing').tolist()[::-1], plot_df['observation_count'].tolist()[::-1], FIGURES_DIR / 'compound_class_distribution.png', 'Compound Class Distribution', color='#bc6c25')
    groups = [(str(row[CLASS]), df.loc[df[CLASS] == row[CLASS], TARGET]) for _, row in plot_df.head(10).iterrows()]
    draw_group_boxplots(groups, FIGURES_DIR / 'retention_by_compound_class.png', 'Retention by Compound Class')
    return summary


def method_outputs(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby(METHOD, dropna=False).agg(
        observation_count=(TARGET, 'size'),
        unique_compounds=(COMPOUND_ID, 'nunique'),
        mean_retention=(TARGET, 'mean'),
        median_retention=(TARGET, 'median'),
        std_retention=(TARGET, 'std'),
        percentage_gt_100=(APPARENT, lambda s: float(s.mean() * 100)),
    ).reset_index().sort_values('observation_count', ascending=False).reset_index(drop=True)
    summary.to_csv(TABLES_DIR / 'cooking_method_summary.csv', index=False)
    groups = [(str(row[METHOD]), df.loc[df[METHOD] == row[METHOD], TARGET]) for _, row in summary.head(12).iterrows()]
    draw_group_boxplots(groups, FIGURES_DIR / 'retention_by_cooking_method.png', 'Retention by Cooking Method')
    return summary


def binned_summary(df: pd.DataFrame, column: str, output_name: str) -> pd.DataFrame:
    numeric = pd.to_numeric(df[column], errors='coerce')
    valid = df.loc[numeric.notna(), [column, TARGET]].copy()
    valid[column] = pd.to_numeric(valid[column], errors='coerce')
    if len(valid) < 4 or valid[column].nunique() < 2:
        out = pd.DataFrame(columns=['bin', 'count', 'mean_retention', 'median_retention'])
    else:
        bins = min(8, max(4, valid[column].nunique()))
        valid['bin'] = pd.cut(valid[column], bins=bins, duplicates='drop')
        out = valid.groupby('bin', observed=False)[TARGET].agg(['count', 'mean', 'median']).reset_index()
        out.columns = ['bin', 'count', 'mean_retention', 'median_retention']
        out['bin'] = out['bin'].astype(str)
    out.to_csv(TABLES_DIR / output_name, index=False)
    return out

def numeric_summary(df: pd.DataFrame, column: str, output_name: str) -> pd.DataFrame:
    series = pd.to_numeric(df[column], errors='coerce')
    stats = series_stats(series, [0.25, 0.75])
    stats['missing_count'] = int(series.isna().sum())
    pd.DataFrame([stats]).to_csv(TABLES_DIR / output_name, index=False)
    return pd.DataFrame([stats])


def descriptor_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    corr_rows = []
    for descriptor in DESCRIPTORS:
        series = pd.to_numeric(df[descriptor], errors='coerce')
        stats = series_stats(series, [0.25, 0.75])
        stats.update({'descriptor': descriptor, 'missing_count': int(series.isna().sum())})
        rows.append(stats)
        pearson_r, pearson_p, pearson_n = correlation_with_p(series, df[TARGET], 'pearson')
        spearman_r, spearman_p, spearman_n = correlation_with_p(series, df[TARGET], 'spearman')
        corr_rows.append({
            'descriptor': descriptor,
            'pearson_r': pearson_r,
            'pearson_p_approx': pearson_p,
            'pearson_n': pearson_n,
            'spearman_r': spearman_r,
            'spearman_p_approx': spearman_p,
            'spearman_n': spearman_n,
            'limitation_note': 'Repeated observations of the same compound violate independence assumptions; correlations are exploratory only.',
        })
    summary = pd.DataFrame(rows)
    summary.to_csv(TABLES_DIR / 'molecular_descriptor_summary.csv', index=False)
    corr_df = pd.DataFrame(corr_rows).sort_values('pearson_r', key=lambda s: s.abs(), ascending=False).reset_index(drop=True)
    corr_df.to_csv(TABLES_DIR / 'descriptor_retention_correlations.csv', index=False)
    draw_barh(corr_df['descriptor'].tolist()[::-1], corr_df['pearson_r'].abs().tolist()[::-1], FIGURES_DIR / 'descriptor_retention_correlations.png', 'Absolute Pearson Correlation with Retention', color='#577590')
    draw_barh(summary['descriptor'].tolist()[::-1], summary['mean'].fillna(0).tolist()[::-1], FIGURES_DIR / 'descriptor_distributions.png', 'Descriptor Mean Values Overview', color='#43aa8b')
    return summary, corr_df


def numerical_correlation_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    available = [c for c in NUMERIC_CORRELATION_FEATURES if c in df.columns]
    numeric = df[available].apply(pd.to_numeric, errors='coerce')
    matrix = numeric.rank(method='average').corr(method='pearson')
    pair_rows = []
    for i, left in enumerate(available):
        for right in available[i + 1:]:
            pair = numeric[[left, right]].dropna()
            if len(pair) < 3:
                continue
            pearson = float(pair[left].corr(pair[right], method='pearson'))
            spearman = float(pair[left].rank(method='average').corr(pair[right].rank(method='average'), method='pearson'))
            pair_rows.append({'feature_1': left, 'feature_2': right, 'n': int(len(pair)), 'pearson_r': pearson, 'spearman_r': spearman, 'max_abs_correlation': max(abs(pearson), abs(spearman)), 'high_correlation_flag': max(abs(pearson), abs(spearman)) >= 0.8})
    long_df = pd.DataFrame(pair_rows).sort_values('max_abs_correlation', ascending=False).reset_index(drop=True)
    long_df.to_csv(TABLES_DIR / 'numerical_feature_correlations.csv', index=False)
    draw_heatmap(matrix, FIGURES_DIR / 'numerical_feature_correlation_heatmap.png', 'Spearman Correlation Heatmap: Numerical Predictors')
    return matrix, long_df


def categorical_outputs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature in CATEGORICAL_FEATURES:
        total = len(df)
        missing = int(df[feature].isna().sum())
        counts = df[feature].fillna('Missing').value_counts(dropna=False)
        for category, count in counts.head(25).items():
            rows.append({'feature': feature, 'category': category, 'count': int(count), 'percentage': float(count / total * 100), 'missing_count': missing, 'missing_percentage': float(missing / total * 100), 'category_count_total': int(df[feature].nunique(dropna=True))})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / 'categorical_feature_summary.csv', index=False)
    return out


def food_outputs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frequency = df.groupby(FOOD, dropna=False).agg(observation_count=(TARGET, 'size'), unique_compounds=(COMPOUND_ID, 'nunique')).reset_index().sort_values('observation_count', ascending=False).reset_index(drop=True)
    frequency.to_csv(TABLES_DIR / 'food_frequency.csv', index=False)
    top_retention = df.groupby(FOOD, dropna=False)[TARGET].agg(['count', 'mean', 'median', 'std', 'min', 'max']).reset_index().sort_values('count', ascending=False).head(20)
    top_retention.to_csv(TABLES_DIR / 'top_foods_retention.csv', index=False)
    draw_barh(frequency.head(20)[FOOD].fillna('Missing').tolist()[::-1], frequency.head(20)['observation_count'].tolist()[::-1], FIGURES_DIR / 'top_foods_by_observations.png', 'Top Foods by Observation Count', color='#f4a261')
    return frequency, top_retention


def missingness_vs_target_outputs(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variable in KEY_MISSINGNESS_COLUMNS:
        marker = df[variable].notna().map({True: 'Reported', False: 'Missing'})
        for group, sub in df.groupby(marker):
            rows.append({'variable': variable, 'group': group, 'count': int(len(sub)), 'group_percent': float(len(sub) / len(df) * 100), 'mean_retention': float(sub[TARGET].mean()), 'median_retention': float(sub[TARGET].median()), 'std_retention': float(sub[TARGET].std(ddof=1)) if len(sub) > 1 else 0.0})
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / 'missingness_vs_retention.csv', index=False)
    draw_missingness_group_comparison(out, FIGURES_DIR / 'missingness_vs_retention.png', 'Retention by Reported vs Missing Status')
    return out


def extreme_observations_outputs(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = [TARGET, 'Temperature_C', 'Cooking_Time_min', *DESCRIPTORS]
    rows = []
    seen = set()
    for column in numeric_columns:
        series = pd.to_numeric(df[column], errors='coerce')
        valid = series.dropna()
        if valid.empty:
            continue
        q1, q3 = valid.quantile([0.25, 0.75]).tolist()
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        base_columns = ['Record_ID', 'Compound_Name', COMPOUND_ID, FOOD, METHOD, 'Temperature_C', 'Cooking_Time_min', TARGET]
        subset = df.loc[(series < low) | (series > high), base_columns].copy()
        subset['extreme_variable'] = column
        subset['rule'] = f'IQR outside [{low:.3f}, {high:.3f}]'
        subset['extreme_value'] = pd.to_numeric(series.loc[(series < low) | (series > high)], errors='coerce').values
        subset = subset.sort_values('extreme_value', ascending=False).head(20)
        for _, row in subset.iterrows():
            key = (row['Record_ID'], column)
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                'Record_ID': row['Record_ID'],
                'Compound_Name': row['Compound_Name'],
                'Canonical_Molecular_ID': row[COMPOUND_ID],
                'Food_Name_Standardized': row[FOOD],
                'Cooking_Method_Standardized': row[METHOD],
                'Temperature_C': row['Temperature_C'],
                'Cooking_Time_min': row['Cooking_Time_min'],
                'Retention_Final': row[TARGET],
                'extreme_variable': column,
                'extreme_value': row['extreme_value'],
                'rule': row['rule'],
            })
    out = pd.DataFrame(rows).sort_values(['extreme_variable', 'extreme_value'], ascending=[True, False]).reset_index(drop=True)
    out.to_csv(TABLES_DIR / 'extreme_observations.csv', index=False)
    return out


def repeated_structure_outputs(freq: pd.DataFrame) -> pd.DataFrame:
    counts = freq['observation_count']
    total_obs = int(counts.sum())
    rows = [
        {'metric': 'total_observations', 'value': total_obs},
        {'metric': 'unique_compounds', 'value': int(len(freq))},
        {'metric': 'observations_from_n_eq_1', 'value': int(counts[counts == 1].sum())},
        {'metric': 'observations_from_n_le_2', 'value': int(counts[counts <= 2].sum())},
        {'metric': 'observations_from_n_le_5', 'value': int(counts[counts <= 5].sum())},
        {'metric': 'observations_from_n_ge_10', 'value': int(counts[counts >= 10].sum())},
        {'metric': 'observations_from_n_ge_20', 'value': int(counts[counts >= 20].sum())},
        {'metric': 'percent_observations_top_5_compounds', 'value': float(freq.head(5)['observation_count'].sum() / total_obs * 100)},
        {'metric': 'percent_observations_top_10_compounds', 'value': float(freq.head(10)['observation_count'].sum() / total_obs * 100)},
        {'metric': 'percent_observations_top_20_compounds', 'value': float(freq.head(20)['observation_count'].sum() / total_obs * 100)},
    ]
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / 'repeated_compound_structure.csv', index=False)
    return out


def potential_issues_summary(missingness_df: pd.DataFrame, repeated_df: pd.DataFrame, descriptor_corr_df: pd.DataFrame) -> list[str]:
    issues = []
    issues.append('Repeated-compound imbalance: top 10 compounds contribute ' + f"{float(repeated_df.loc[repeated_df['metric']=='percent_observations_top_10_compounds','value'].iloc[0]):.1f}% of observations")
    issues.append('Sparse predictors: ' + ', '.join(missingness_df.head(3)['column'].tolist()))
    issues.append('Apparent increases preserved: retention >100% observations remain in the dataset')
    if not descriptor_corr_df.empty:
        issues.append('Descriptor-retention correlations are exploratory only because repeated compounds violate independence assumptions')
    return issues


def build_report(overview: dict, missingness_df: pd.DataFrame, retention_stats: dict, apparent_df: pd.DataFrame, top_retention: pd.DataFrame, freq_stats: dict, class_df: pd.DataFrame, method_df: pd.DataFrame, temp_df: pd.DataFrame, time_df: pd.DataFrame, descriptor_df: pd.DataFrame, descriptor_corr_df: pd.DataFrame, numeric_pairs_df: pd.DataFrame, food_freq_df: pd.DataFrame, missing_target_df: pd.DataFrame, repeated_df: pd.DataFrame, issues: list[str]) -> None:
    strongest_pearson = descriptor_corr_df.iloc[descriptor_corr_df['pearson_r'].abs().argmax()]['descriptor'] if not descriptor_corr_df.empty else 'None'
    strongest_spearman = descriptor_corr_df.iloc[descriptor_corr_df['spearman_r'].abs().argmax()]['descriptor'] if not descriptor_corr_df.empty else 'None'
    lines = [
        '# CookRisk Exploratory Data Analysis', '',
        '## 1. Dataset Overview', '', markdown_table(pd.DataFrame([overview])), '',
        '## 2. Data Quality', '', '- The input dataset was read only from `data/preprocessing/final/cookchem_molecular_retention_preprocessed.csv`.', '- No imputation, filtering, scaling, encoding, or model training was performed.', '',
        '## 3. Missingness', '', markdown_table(missingness_df.head(15)), '',
        '## 4. Retention Distribution', '', markdown_table(pd.DataFrame([retention_stats])), '',
        '## 5. Apparent Increase (>100%) Analysis', '', markdown_table(apparent_df), '',
        '## 6. Extreme Retention Values', '', markdown_table(top_retention), '',
        '## 7. Compound Frequency and Repetition', '', markdown_table(pd.DataFrame([freq_stats])), '', markdown_table(repeated_df), '',
        '## 8. Compound Classes', '', markdown_table(class_df.head(15)), '',
        '## 9. Cooking Methods', '', markdown_table(method_df.head(15)), '',
        '## 10. Temperature', '', markdown_table(temp_df), '',
        '## 11. Cooking Time', '', markdown_table(time_df), '',
        '## 12. Molecular Descriptors', '', markdown_table(descriptor_df), '',
        '## 13. Descriptor-Retention Relationships', '', markdown_table(descriptor_corr_df), '', '- Pearson and Spearman p-values are approximate Fisher-z two-sided values because `scipy` is unavailable in the runtime.', '- Repeated observations of the same compound violate independence assumptions, so these correlations are exploratory only.', '',
        '## 14. Numerical Feature Correlations', '', markdown_table(numeric_pairs_df.head(20)), '',
        '## 15. Food Distribution', '', markdown_table(food_freq_df.head(20)), '',
        '## 16. Missingness vs Retention', '', markdown_table(missing_target_df), '',
        '## 17. Important EDA Findings', ''
    ]
    lines.extend([f'- {issue}' for issue in issues])
    lines.extend(['', '## 18. Potential Problems', '', '- High missingness in process-condition variables may make naive row-level comparisons misleading.', '- Observation-level counts substantially exceed unique-compound counts, so many rows are repeated compounds rather than independent molecular identities.', '', '## 19. Implications for ML', '', '- Compound-level grouped validation will matter because repeated compounds dominate parts of the dataset.', '- Apparent increases should remain in the response variable and be investigated scientifically, not capped mechanically.', '- Descriptor-retention relationships should be re-evaluated later with grouped validation rather than ordinary row-level assumptions.', '', '## 20. Recommended Next Steps', '', '- Use this EDA as the read-only baseline for grouped validation design.', '- Regenerate molecular-feature stage outputs against the current 1124-row preprocessing output before downstream modeling.', '- Review high-missingness predictors and decide later whether each should be modeled, grouped, or left out in specific experiments.', ''])
    REPORT_PATH.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(INPUT_PATH)
    overview = overview_outputs(df)
    missingness_df = missingness_outputs(df)
    retention_stats = retention_outputs(df)
    apparent_df = apparent_increase_outputs(df)
    top_retention = top_retention_outputs(df)
    freq_df, freq_stats, top_compounds = compound_frequency_outputs(df)
    compound_retention_outputs(df, top_compounds)
    class_df = class_outputs(df)
    method_df = method_outputs(df)
    temp_df = numeric_summary(df, 'Temperature_C', 'temperature_summary.csv')
    binned_summary(df, 'Temperature_C', 'retention_by_temperature_bins.csv')
    draw_histogram(df['Temperature_C'], FIGURES_DIR / 'temperature_distribution.png', 'Temperature Distribution')
    draw_scatter(df['Temperature_C'], df[TARGET], FIGURES_DIR / 'retention_vs_temperature.png', 'Retention vs Temperature', 'Temperature_C', TARGET)
    time_df = numeric_summary(df, 'Cooking_Time_min', 'cooking_time_summary.csv')
    binned_summary(df, 'Cooking_Time_min', 'retention_by_cooking_time_bins.csv')
    draw_histogram(df['Cooking_Time_min'], FIGURES_DIR / 'cooking_time_distribution.png', 'Cooking Time Distribution')
    draw_scatter(df['Cooking_Time_min'], df[TARGET], FIGURES_DIR / 'retention_vs_cooking_time.png', 'Retention vs Cooking Time', 'Cooking_Time_min', TARGET)
    descriptor_df, descriptor_corr_df = descriptor_outputs(df)
    _, numeric_pairs_df = numerical_correlation_outputs(df)
    categorical_outputs(df)
    food_freq_df, _ = food_outputs(df)
    missing_target_df = missingness_vs_target_outputs(df)
    extreme_observations_outputs(df)
    repeated_df = repeated_structure_outputs(freq_df)
    issues = potential_issues_summary(missingness_df, repeated_df, descriptor_corr_df)
    build_report(overview, missingness_df, retention_stats, apparent_df, top_retention, freq_stats, class_df, method_df, temp_df, time_df, descriptor_df, descriptor_corr_df, numeric_pairs_df, food_freq_df, missing_target_df, repeated_df, issues)

    strongest_pearson = descriptor_corr_df.iloc[descriptor_corr_df['pearson_r'].abs().argmax()] if not descriptor_corr_df.empty else None
    strongest_spearman = descriptor_corr_df.iloc[descriptor_corr_df['spearman_r'].abs().argmax()] if not descriptor_corr_df.empty else None
    top_compound = freq_df.iloc[0]
    top_method = method_df.iloc[0]
    summary = {
        'observations': int(len(df)),
        'unique_compounds': int(df[COMPOUND_ID].nunique(dropna=True)),
        'columns': int(len(df.columns)),
        'target_statistics': retention_stats,
        'retention_gt_100_count': int(df[APPARENT].sum()),
        'retention_gt_100_percentage': float(df[APPARENT].mean() * 100),
        'most_frequent_compound': {'canonical_molecular_id': top_compound[COMPOUND_ID], 'canonical_compound_name': top_compound[COMPOUND_NAME], 'observation_count': int(top_compound['observation_count'])},
        'most_frequent_cooking_method': {'cooking_method_standardized': top_method[METHOD], 'observation_count': int(top_method['observation_count'])},
        'most_missing_predictor': missingness_df.iloc[0]['column'],
        'strongest_descriptor_pearson': None if strongest_pearson is None else {'descriptor': strongest_pearson['descriptor'], 'pearson_r': float(strongest_pearson['pearson_r']), 'p_value_approx': None if pd.isna(strongest_pearson['pearson_p_approx']) else float(strongest_pearson['pearson_p_approx'])},
        'strongest_descriptor_spearman': None if strongest_spearman is None else {'descriptor': strongest_spearman['descriptor'], 'spearman_r': float(strongest_spearman['spearman_r']), 'p_value_approx': None if pd.isna(strongest_spearman['spearman_p_approx']) else float(strongest_spearman['spearman_p_approx'])},
        'potential_major_issues': issues,
    }
    save_json(SUMMARIES_DIR / 'eda_summary.json', summary)

    print('========================================')
    print('COOKRISK EDA COMPLETE')
    print('========================================')
    print()
    print(f'Input: {INPUT_PATH.relative_to(ROOT)}')
    print()
    print(f'Observations: {len(df)}')
    print()
    print(f'Unique compounds: {df[COMPOUND_ID].nunique(dropna=True)}')
    print()
    print(f'Columns: {len(df.columns)}')
    print()
    print(f'Retention mean: {retention_stats["mean"]:.4f}')
    print()
    print(f'Retention median: {retention_stats["median"]:.4f}')
    print()
    print(f'Retention >100%: {int(df[APPARENT].sum())} ({df[APPARENT].mean() * 100:.2f}%)')
    print()
    print(f'Most frequent compound: {top_compound[COMPOUND_NAME]} ({top_compound[COMPOUND_ID]}) [{int(top_compound["observation_count"])} observations]')
    print()
    print(f'Most frequent cooking method: {top_method[METHOD]} [{int(top_method["observation_count"])} observations]')
    print()
    print(f'Most missing predictor: {missingness_df.iloc[0]["column"]}')
    print()
    print(f'Descriptor with strongest Pearson relationship: {strongest_pearson["descriptor"] if strongest_pearson is not None else "None"}')
    print()
    print(f'Descriptor with strongest Spearman relationship: {strongest_spearman["descriptor"] if strongest_spearman is not None else "None"}')
    print()
    print('Potential major issues: ' + '; '.join(issues))
    print()
    print(f'EDA report: {REPORT_PATH.relative_to(ROOT)}')
    print()
    print(f'Figures: {FIGURES_DIR.relative_to(ROOT)}')
    print()
    print(f'Tables: {TABLES_DIR.relative_to(ROOT)}')


if __name__ == '__main__':
    main()




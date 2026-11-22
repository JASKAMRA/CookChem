"""Presentation-only helpers shared by the CookRisk Streamlit pages."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_EXCLUDED_PRESENTATION_MARKERS = (
    "friend-claim", "friend-reported r", "friend claim", ".3301", ".2990",
)


def _contains_excluded_claim(value: Any) -> bool:
    text = str(value).casefold()
    return any(marker in text for marker in _EXCLUDED_PRESENTATION_MARKERS)


def filter_table_for_display(data: Any) -> Any:
    """Return a display copy with the unsupported friend-claim entry removed.

    The input evidence remains untouched. For dataframe-like objects this uses
    their copy/loc interface; list rows are copied before being passed onward.
    """
    if isinstance(data, list):
        displayed = []
        for row in data:
            if isinstance(row, Mapping):
                if any(_contains_excluded_claim(value) for value in row.values()):
                    continue
                visible_row = {key: value for key, value in row.items()
                               if not _contains_excluded_claim(key)}
                if visible_row:
                    displayed.append(visible_row)
            elif not _contains_excluded_claim(row):
                displayed.append(row)
        return displayed

    if all(hasattr(data, attribute) for attribute in ("columns", "astype", "loc", "copy")):
        columns = [column for column in data.columns if not _contains_excluded_claim(column)]
        if not len(data.index):
            return data.loc[:, columns].copy()
        text = data.astype("string")
        row_mask = text.apply(
            lambda column: column.str.contains(
                r"friend-claim|friend-reported r|friend claim|\.3301|\.2990",
                case=False, regex=True, na=False
            )
        ).any(axis=1)
        return data.loc[~row_mask, columns].copy()

    return data


def is_excluded_claim_entry(record: Mapping[str, Any]) -> bool:
    """Identify an excluded claim entry in a presentation-only record."""
    return any(_contains_excluded_claim(key) or _contains_excluded_claim(value)
               for key, value in record.items())


def show_dataframe(data: Any, **kwargs: Any) -> Any:
    """Render a dataframe after filtering only the excluded claim from its view."""
    import streamlit as st

    return st.dataframe(filter_table_for_display(data), **kwargs)

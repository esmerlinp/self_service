from __future__ import annotations

import json
import os
import streamlit.components.v1 as components

_RELEASE = True
import pandas as pd

if not _RELEASE:
    _component_func = components.declare_component(
        "dataframe_with_button",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("dataframe_with_button", path=build_dir)


def static_dataframe(
    data: pd.DataFrame,
    clickable_column: str,
    key=None,
):
    """
    Custom Data Frame with clickable column functionality.

    Parameters
    ----------
    data : pd.DataFrame
        The input DataFrame to render.
    clickable_column : str
        The name of the column to make clickable. Must contain unique strings.
    key : str, optional
        Streamlit's widget key.

    Returns
    -------
    dict
        Returns the button clicked.
    """
    if clickable_column not in data.columns:
        raise ValueError(f"Column '{clickable_column}' does not exist in the DataFrame.")

    if not data[clickable_column].is_unique:
        raise ValueError(f"Column '{clickable_column}' doesn't contain unique values.")

    data_json = data.to_json(orient="records")

    result = _component_func(
        data_json=data_json, clickable_column=clickable_column, key=key
    )
    if result is not None:
        return result["button"]
    else:
        return None

def editable_dataframe(
    data: pd.DataFrame,
    clickable_column: str,
    key=None,
):
    if clickable_column not in data.columns:
        raise ValueError(f"Column '{clickable_column}' does not exist in the DataFrame.")

    if not data[clickable_column].is_unique:
        raise ValueError(f"Column '{clickable_column}' doesn't contain unique values.")

    # Extract categorical columns and their categories
    categorical_info = {
        col: data[col].cat.categories.tolist()
        for col in data.select_dtypes(include=["category"]).columns
    }

    data_json = data.to_json(orient="records")

    result = _component_func(
        data_json=data_json,
        clickable_column=clickable_column,
        categorical_info=categorical_info,
        key=key,
        editable=True,
    )
    if result is not None:
        return result["data"], result["button"]
    else:
        return json.loads(data_json), None

from __future__ import annotations

import json

import pandas as pd
import plotly.graph_objects as go

from .series import SeriesDefinition


def build_series_figure(definition: SeriesDefinition, frame: pd.DataFrame) -> go.Figure:
    ordered = frame.sort_values("date")
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=ordered["date"],
            y=ordered["value"],
            mode="lines+markers",
            line={"width": 2, "color": "#0d5c63"},
            marker={"size": 5, "color": "#f05d23"},
            name=definition.title,
        )
    )
    figure.update_layout(
        template="plotly_white",
        title=definition.title,
        margin={"l": 48, "r": 24, "t": 60, "b": 48},
        hovermode="x unified",
    )
    figure.update_xaxes(title_text="Data")
    figure.update_yaxes(title_text=definition.unit)
    return figure


def figure_as_dict(figure: go.Figure) -> dict:
    return json.loads(figure.to_json())
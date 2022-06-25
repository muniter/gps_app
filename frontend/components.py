import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
from dash.development.base_component import Component


def map_figure(data: pd.DataFrame, vehicle_name: str = "") -> go.Figure:
    fig = go.Figure(
        data=go.Scattermapbox(
            lon=data.longitude,
            lat=data.latitude,
            mode="markers",
            text=vehicle_name or data.vehicle_name,
        )
    )

    fig.update_layout(
        hovermode="closest",
        mapbox_style="open-street-map",
        mapbox=dict(
            center=go.layout.mapbox.Center(
                lat=data.latitude.mean(),
                lon=data.longitude.mean(),
            ),
            bearing=0,
            pitch=0,
            zoom=5,  # TODO: make this smarter
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


def new_toast(base: list, message: str):
    toast = dbc.Toast(
        children=[
            html.P(
                children=message,
                className="mb-0",
                id="toast-message",
            )
        ],
        id="auto-toast",
        header="This is the header",
        icon="primary",
        duration=4000,
        is_open=True,
    )
    return [toast]

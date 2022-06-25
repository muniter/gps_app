import dash
from dash import Dash, html, dcc, Input, Output
from dash.exceptions import PreventUpdate
from pandas.core.frame import DataFrame
import requests
import os
import json
import typing
import dash_bootstrap_components as dbc
import numpy as np

from . import components
from . import data
from datetime import date

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

ALL_VEH = "All - Last Report"

DATA = data.last_records

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            justify="center",
            children=[
                dbc.Col(width="auto", children=html.H1("DS4A Gps Application")),
            ],
        ),
        html.Br(),
        dbc.Row(
            justify="center",
            children=dbc.Col(
                children=[
                    dbc.Row(
                        justify="center",
                        children=[
                            dbc.Col(
                                width="auto",
                                children=dbc.Row(
                                    [
                                        dbc.Col(
                                            dcc.Dropdown(
                                                [ALL_VEH]
                                                + data.vehicles["name"].to_list(),
                                                ALL_VEH,
                                                id="vehicle_name",
                                                className="col col-auto",
                                            )
                                        ),
                                        dcc.DatePickerRange(
                                            id="date_range",
                                            className="col col-auto",
                                            start_date=data.general["date_range"][
                                                "start"
                                            ],
                                            end_date=data.general["date_range"]["end"],
                                        ),
                                    ]
                                ),
                            )
                        ],
                    ),
                    html.Br(),
                    dbc.Row(
                        children=[
                            dbc.Col(
                                dcc.Loading(
                                    type="default",
                                    children=dcc.Graph(
                                        id="map-graph",
                                        figure=components.map_figure(DATA),
                                        style={"height": "90vh"},
                                    ),
                                )
                            ),
                        ]
                    ),
                ]
            ),
        ),
        html.Div(children=[], id="toast-container", style={"position": "absolute", "top": 10, "right": 0, "min-height": "200px"}),
    ],
)


@app.callback(
    Output("map-graph", "figure"),
    Output("toast-container", "children"),
    Input("vehicle_name", "value"),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
    Input("toast-container", "children"),
)
def update_map(vehicle_name, start_date, end_date, toast):
    res: DataFrame
    last_record = False
    if vehicle_name == ALL_VEH:
        last_record = True
        res = data.last_records
    else:
        res = data.get_vehicle_data(vehicle_name, start_date, end_date)

    if res.empty:
        toast = components.new_toast(
            toast, f"No data found for vehicle {vehicle_name} on the given dates"
        )
        return dash.no_update, toast
    else:
        # Keep the global DATA updated
        DATA = res
        fig = components.map_figure(
            data=DATA,
            vehicle_name= '' if last_record else vehicle_name,
        )

        return fig, dash.no_update


if __name__ == "__main__":
    app.run_server(debug=True)

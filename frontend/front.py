import os
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from pandas.core.frame import DataFrame
import dash_bootstrap_components as dbc

from . import components
from . import data
from . import app

CURRENT_VEH = "WEV489"
DATA = data.get_vehicle_data(
    CURRENT_VEH, data.general["date_range"]["start"], data.general["date_range"]["end"]
)
PREV_VALS = {}


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
        # Configuration, dropdowns and buttons
        dbc.Row(
            justify="center",
            children=[
                dbc.Col(
                    class_name="col-6",
                    children=dcc.Dropdown(
                        options=data.vehicles["name"].to_list(),
                        value=CURRENT_VEH,
                        id="vehicle-name",
                    ),
                ),
                dbc.Col(
                    class_name="col-4",
                    children=dcc.DatePickerRange(
                        id="date-range",
                        start_date=data.general["date_range"]["start"],
                        end_date=data.general["date_range"]["end"],
                    ),
                ),
            ],
        ),
        dbc.Row(
            justify="center",
            children=dbc.Col(
                dbc.Button(
                    "Update",
                    id="update_button",
                    color="primary",
                    className="mr-1",
                ),
                width="auto",
            ),
        ),
        html.Br(),
        # Graph
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        html.H2("Route Map"),
                        dcc.Loading(
                            dcc.Graph(
                                id="map-graph",
                            ),
                        )
                    ]
                ),
            ]
        ),
        html.Br(),
        html.Div(
            id="extra-reports",
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(
                            children=[
                                html.H2("Speed Map"),
                                dcc.Loading(
                                    dcc.Graph(
                                        id="speed-graph",
                                    ),
                                ),
                            ]
                        ),
                    ]
                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            children=[
                                html.H2("Distance Traveled"),
                                dcc.Loading(
                                    dcc.Graph(
                                        id="distance-graph",
                                    ),
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        ),
        # Toaster
        html.Div(
            children=[],
            id="toast-container",
            style={
                "position": "absolute",
                "top": 10,
                "right": 0,
                "min-height": "200px",
            },
        ),
    ],
)


def update_state(vehicle, data):
    global CURRENT_VEH
    global DATA
    CURRENT_VEH = vehicle
    DATA = data


@app.callback(
    Output("map-graph", "figure"),
    Output("toast-container", "children"),
    State("vehicle-name", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    Input("update_button", "n_clicks"),
)
def update_map(vehicle_name, start_date, end_date, _):
    res: DataFrame
    res = data.get_vehicle_data(vehicle_name, start_date, end_date)

    if res.empty:
        toast = components.new_toast(
            f"No data found for vehicle {vehicle_name} on the given dates, showing previous data."
        )
        return PREV_VALS["figure"], toast
    else:
        # Keep the global DATA updated
        update_state(vehicle=vehicle_name, data=res)
        fig = components.map_figure(data=DATA)
        PREV_VALS["figure"] = fig

        return fig, components.new_toast("Vehicle data updated")


@app.callback(
    Output("vehicle-name", "value"),
    Output("date-range", "start_date"),
    Output("date-range", "end_date"),
    State("vehicle-name", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    Input("map-graph", "figure"),
)
def update_inputs(vehicle_name, start_date, end_date, _):
    if CURRENT_VEH != vehicle_name:
        print("Current vehicle is", CURRENT_VEH, "and the new one is", vehicle_name)
        return PREV_VALS["vehicle-name"], PREV_VALS["start_date"], PREV_VALS["end_date"]
    else:
        PREV_VALS["vehicle-name"] = vehicle_name
        PREV_VALS["start_date"] = start_date
        PREV_VALS["end_date"] = end_date
        raise PreventUpdate


@app.callback(
    Output("distance-graph", "figure"),
    Input("map-graph", "figure"),
)
def update_distance_figure(_):
    return components.distance_traveled_figure(DATA)


@app.callback(
    Output("speed-graph", "figure"),
    Input("map-graph", "figure"),
)
def update_speed_figure(_):
    return components.speed_map_figure(DATA)


if __name__ == "__main__":
    app.run(debug=os.environ.get('ENV') != 'production')


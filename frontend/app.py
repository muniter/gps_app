import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import urllib.parse
from dash.dependencies import Output, Input, State
from dash import dash_table
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine
from datetime import date, datetime
import requests
import plotly.express as px

import plotly.graph_objects as go

# __________________________________________________________database
user = "postgres"
password = urllib.parse.quote_plus(
    "Ltxf9%dTJPfNL#Xrzn@*rjy24^UY!^7^^j7xvfppPwcFKpW^f7VBJc^8p@izP*z#fq397Xj^3J7&r@RokHkhW%3yT5t96c@$a5&c$@dUPKQ"
)
port = "5432"
db_name = "database"
hostname = "ds4a_db.muniter.xyz"
DB_URL = f"postgresql://{user}:{password}@{hostname}:{port}/{db_name}"
engine = create_engine(DB_URL)
# __________________________________________________________________

# verificar los carros
vehicles = pd.read_sql_query("SELECT * FROM vehicle;", engine)

table_params1 = {
    "title": "Users",
    "description": "Tabla de lista de usuarios",
    "columns": ["id", "latitude", "longitude", "speed", "datetime"],
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Vehicle statistics"

parrafo1 = (
    "Analyzes different parameters for each of the vehicles stored in the database"
)

app.layout = dbc.Container(
    children=[
        dbc.Col(
            children=[
                html.P(children="🚗", className="header-emoji"),
                html.H1(children="Vehicle statistics", className="header-title"),
                html.P(
                    children=parrafo1,
                    className="header-description",
                ),
            ],
            className="header",
        ),
        #############################################################################################3
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(children="Vehicle Name", className="menu-title"),
                        dcc.Dropdown(
                            id="vehicle-filter",
                            options=[
                                {"label": name, "value": name}
                                for name in np.sort(vehicles.name.unique())
                            ],
                            value="0002",
                            clearable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        html.Div(children="Group By", className="menu-title"),
                        dcc.Dropdown(
                            id="groupBy",
                            options=["first day", "last day", "date range"],
                            value="date range",
                            clearable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        html.Div(
                            children="Date Range (dd-mm-yyyy)", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=date(2022, 1, 1),  # yyyy,mm,dd
                            end_date=date(2022, 6, 7),
                            display_format="DD-MM-Y"
                            # display_format = "Y-MM-DD"
                        ),
                    ],
                ),
                dbc.Col(
                    [
                        html.Div(children="Show Tables", className="show-tables"),
                        dcc.Dropdown(
                            id="show_tables",
                            options=["yes", "no"],
                            value="yes",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.P("Filter by speed :"),
                dcc.RangeSlider(
                    id="speed-slider",
                    min=0,
                    max=150,
                    step=1,
                    marks={0: "0", 150: "150"},
                    value=[0, 150],
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                html.Div(children="Update Information", className="menu-title"),
                dbc.Button(
                    id="submit-button-state",
                    children="Update",
                    outline=True,
                    color="dark",
                    className="d-grid gap-2 col-6 mx-auto",
                ),
                html.Div(id="output-date-picker-range"),
            ],
            className="card-menu",
        ),
        #############################################################################################
        dbc.Col(
            [
                dbc.Row(
                    [
                        html.P("Data information:"),
                        html.Div(
                            children=dcc.Graph(
                                id="speed-chart", config={"displayModeBar": True}
                            )
                        ),
                        dash_table.DataTable(
                            id="table1_out",
                            data=[],
                            columns=[],
                            page_size=7,
                            style_table={"overflowX": "auto"},
                            style_cell={
                                # all three widths are needed
                                "minWidth": "100px",
                                "width": "100px",
                                "maxWidth": "100px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                            },
                        ),
                    ],
                    className="card",
                ),
                dbc.Row(
                    [
                        html.P("map by day of week:"),
                        html.Div(
                            children=dcc.Graph(
                                id="volume-chart",
                                config={"displayModeBar": True},
                            )
                        ),
                    ],
                    className="card",
                ),
                dbc.Row(
                    [
                        html.P("map by speed:"),
                        html.Div(
                            children=dcc.Graph(
                                id="speed-heat-chart",
                                config={"displayModeBar": True},
                            )
                        ),
                    ],
                    className="card",
                ),
            ]
        ),
    ]
)


@app.callback(
    [
        Output("speed-chart", "figure"),
        Output("volume-chart", "figure"),
        Output("speed-heat-chart", "figure"),
        Output("table1_out", "data"),
        Output("table1_out", "columns"),
        Output("output-date-picker-range", "children"),
        Input("submit-button-state", component_property="n_clicks"),
        Input("show_tables", "value"),
        State("vehicle-filter", "value"),
        State("groupBy", "value"),
        State("date-range", "start_date"),
        State("date-range", "end_date"),
        State("speed-slider", "value"),
    ],
)
def update_charts(
    n_clicks, table_status, name, groupBy, start_date, end_date, slider_range
):
    data_display = ""

    if n_clicks is None:
        raise PreventUpdate

    else:

        # traer informacion de la BD
        url = "https://ds4a-api.muniter.xyz/record/"
        car_name = name + "/"
        initial_date = str(start_date) + "T00:00:00" + "/"
        final_date = str(end_date) + "T00:00:00"
        get_car = url + car_name + initial_date + final_date
        data = requests.get(get_car).json()
        record = pd.DataFrame(data)
        size = record.shape[0]

        if record.empty:
            # aplica si no hay informacion en el query para que las graficas esten vacias

            record["date"] = ""
            record["speed"] = ""
            record["longitude"] = ""
            record["hours"] = ""

            price_chart_figure = blank_fig()
            volume_chart_figure = blank_fig()
            day_week_graph = blank_fig()

            table1_columns = []
            table1_data = []

        else:

            # separa los dias y las horas
            record[["date", "hours"]] = record["datetime"].str.split(
                "T", 1, expand=True
            )
            record["date"] = pd.to_datetime(record["date"])

            # actualiza el camplo a dd-mm-yyyy
            record["date"] = record["date"].dt.strftime("%d-%m-%Y")
            record = record.sort_values(["date", "hours"])

            # para filtrar en df
            datetime_obj = datetime.strptime(start_date, "%Y-%m-%d")
            new_start_date = datetime_obj.strftime("%d-%m-%Y")

            datetime_obj2 = datetime.strptime(end_date, "%Y-%m-%d")
            new_end_date = datetime_obj2.strftime("%d-%m-%Y")

            record["day_week"] = pd.to_datetime(record["date"])
            record["day_week"] = record["day_week"].dt.day_of_week

            y_plot = "speed"
            size_val = "speed"
            color_val = "speed"

            if groupBy == "date range":
                df = record.copy()
                x_plot = "date"

            elif groupBy == "first day":

                df = record[(record["date"] == new_start_date)]
                x_plot = "hours"

            elif groupBy == "last day":
                df = record[(record["date"] == new_end_date)]
                x_plot = "hours"

            # utilizado para filtrar por velocidades
            low, high = slider_range
            mask = (df["speed"] > low) & (df["speed"] < high)
            df = df[mask]

            if table_status == "yes":
                table1_columns = [{"name": i, "id": i} for i in df.columns]
                table1_data = df.to_dict("records")
            else:
                table1_columns = []
                table1_data = []

            price_chart_figure = create_figure_scatter(df, x_plot, y_plot, color_val)

            color = "#E12D39"
            title = "filtered speed and data"
            hovertemplateinfo = "m/s"
            type = "lines"

            # px.set_mapbox_access_token(open(".mapbox_token").read())
            volume_chart_figure = px.scatter_mapbox(
                df,
                lat="latitude",
                lon="longitude",
                color="day_week",
                mapbox_style="open-street-map",
            )

            # volume_chart_figure = create_figure_line(df, x_plot, y_plot, type, hovertemplateinfo, title, color)

            # day_week_graph = px.density_mapbox(df, lat='latitude', lon='longitude', z='speed', radius=10,mapbox_style='open-street-map')

            day_week_graph = px.scatter_mapbox(
                df,
                lat="latitude",
                lon="longitude",
                color="speed",
                size="speed",
                mapbox_style="open-street-map",
                color_continuous_scale=px.colors.cyclical.IceFire,
            )

        return (
            price_chart_figure,
            volume_chart_figure,
            day_week_graph,
            table1_data,
            table1_columns,
            data_display,
        )


# _______________________________________________________________________________________________________________________________
def create_figure_scatter(df, x_plot, y_plot, color_val):

    fig = px.scatter(
        df,
        x=x_plot,
        y=y_plot,
        # size=size_val,
        marginal_x="histogram",
        marginal_y="violin",
        color=color_val,
    )
    return fig


def create_figure_line(df, x_plot, y_plot, type, hovertemplateinfo, title, color):

    x_plot = df[x_plot]
    y_plot = df[y_plot]

    chart_figure = {
        "data": [
            {
                "x": x_plot,
                "y": y_plot,
                "type": type,
                "hovertemplate": "%{y:.2f}" + hovertemplateinfo + "<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": title,
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "", "fixedrange": True},
            "colorway": [color],
        },
    }
    return chart_figure


def blank_fig():
    fig = px.scatter(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

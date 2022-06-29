import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import html
import dash_bootstrap_components as dbc
from dash.development.base_component import Component
import numpy as np


def map_figure(data: pd.DataFrame, vehicle_name: str = "") -> go.Figure:
    fig = go.Figure(
        data=go.Scattermapbox(
            lon=data.longitude,
            lat=data.latitude,
            mode="markers",
            text=vehicle_name or data.vehicle_name,
        )
    )

    zoom, center = zoom_center(lons=data.longitude, lats=data.latitude)
    fig.update_layout(
        hovermode="closest",
        mapbox_style="open-street-map",
        mapbox=dict(
            center=center,
            bearing=0,
            pitch=0,
            zoom=zoom
        ),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


def new_toast(message: str):
    toast = dbc.Toast(
        children=[
            html.P(
                children=message,
                className="mb-0",
                id="toast-message",
            )
        ],
        id="auto-toast",
        header="Notification",
        icon="primary",
        duration=4000,
        is_open=True,
    )
    return [toast]


def zoom_center(
    lons: tuple|None = None,
    lats: tuple|None = None,
    lonlats: tuple|None = None,
    format: str = "lonlat",
    projection: str = "mercator",
    width_to_height: float = 2.0,
) -> (float, dict):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434

    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    lonlats: tuple, optional, gps locations
    format: str, specifying the order of longitud and latitude dimensions,
        expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
        used to select the constrained axis.

    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """
    if lons is None and lats is None:
        if isinstance(lonlats, tuple):
            lons, lats = zip(*lonlats)
        else:
            raise ValueError("Must pass lons & lats or lonlats")

    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        "lon": round((maxlon + minlon) / 2, 6),
        "lat": round((maxlat + minlat) / 2, 6),
    }

    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array(
        [
            0.0007,
            0.0014,
            0.003,
            0.006,
            0.012,
            0.024,
            0.048,
            0.096,
            0.192,
            0.3712,
            0.768,
            1.536,
            3.072,
            6.144,
            11.8784,
            23.7568,
            47.5136,
            98.304,
            190.0544,
            360.0,
        ]
    )

    if projection == "mercator":
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width, lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(f"{projection} projection is not implemented")

    return zoom, center

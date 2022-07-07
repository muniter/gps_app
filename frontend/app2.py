from . import app
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
from sklearn.cluster import KMeans
import plotly.graph_objects as go

#__________________________________________________________database
user = 'postgres'
password = urllib.parse.quote_plus('Ltxf9%dTJPfNL#Xrzn@*rjy24^UY!^7^^j7xvfppPwcFKpW^f7VBJc^8p@izP*z#fq397Xj^3J7&r@RokHkhW%3yT5t96c@$a5&c$@dUPKQ')
port = '5432'
db_name = 'database'
hostname = 'ds4a_db.muniter.xyz'
DB_URL = f"postgresql://{user}:{password}@{hostname}:{port}/{db_name}"
engine = create_engine(DB_URL)
#__________________________________________________________________

#verificar los carros 
vehicles = pd.read_sql_query("SELECT * FROM vehicle;", engine)

table_params1 = {
            'title': 'Users', 
            'description': 'Tabla de lista de usuarios',
            'columns': ['id', 'latitude', 'longitude', 'speed','datetime']
}

app.title = "Vehicle statistics"

parrafo1="Analyzes different parameters for each of the vehicles stored in the database"

app.layout = dbc.Container(

    children=[
        dbc.Col(
            children=[
                html.P(children="🚗", className="header-emoji"),
                html.H1(children="Vehicle statistics", className="header-title"),
                html.P(children=parrafo1, className="header-description",),
                     ], className="header",       
                ),
#############################################################################################3                
        dbc.Row([
        
            dbc.Col([
                        html.Div(children="Vehicle Name", className="menu-title"),
                        dcc.Dropdown(id="vehicle-filter",
                        
                            options=[
                                {"label": name, "value": name}
                                for name in np.sort(vehicles.name.unique())
                                    ],
                                    
                            value="0002",
                            clearable=False,
                            className="dropdown",
                                     ),          
                    ],),
                    
             dbc.Col([
                        html.Div(children="Group By", className="menu-title"),
                        dcc.Dropdown(
                            id="groupBy",
                             options=["first day", "date range"],  
                            value="date range",
                            clearable=False,
                            className="dropdown",
                                     ),
                        
                    ],),
                                    
                dbc.Col([
                
                        html.Div(children="Date Range (dd-mm-yyyy)", className="menu-title"),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=date(2022, 1, 1), #yyyy,mm,dd
                            end_date=date(2022, 6, 7),
                            display_format = "DD-MM-Y"
                            #display_format = "Y-MM-DD"
                                           ),
                        ],),
                       
                dbc.Col([

                     html.Div(children="Show Tables", className="show-tables"),
                        dcc.Dropdown(
                            id="show_tables",
                            options=["yes", "no"],  
                            value="yes",
                            clearable=False,
                            className="dropdown",
                                     ),
                   
                        ]),
                
                html.P("Filter by speed :"),                
                dcc.RangeSlider(
                id='speed-slider',
                min=0, max=150, step=1,
                marks={0: '0', 150: '150'},
                value=[0, 150],
                tooltip={"placement": "bottom", "always_visible": True}
                ),

                html.Div(children="Update Information", className="menu-title"),
                dbc.Button(id='submit-button-state', children='Update',  outline=True, color="dark",  className="d-grid gap-2 col-6 mx-auto"),                                          
                
                html.Div(id='output-date-picker-range')                
                ],className="card-menu",
                ),
#############################################################################################                        
        dbc.Col([
            dbc.Row([
                html.H2("Data information:"),
                html.Div(children=dcc.Graph(id="speed-chart", config={"displayModeBar": True})),
                dash_table.DataTable(id='table1_out',data=[], columns=[], page_size=7,
                style_table={'overflowX': 'auto'},
                style_cell={
                # all three widths are needed
                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                            }),
                ],className="card",),
                
                
                dbc.Row([
                html.H2("Map by day of week(Monday, Tuesday, Wednesday, ...):"),
                html.Div(children=dcc.Graph(id="volume-chart", config={"displayModeBar": True},)),
                ],className="card",),
                
            dbc.Row([
                html.H2("Heatmap speed:"),
                html.Div(children=dcc.Graph(id="speed-heat-chart", config={"displayModeBar": True},)),
                ],className="card",),
                
            dbc.Row([
                html.H2("Route Map:"),
                html.Div(children=dcc.Graph(id="route-map", config={"displayModeBar": True},)),
                ],className="card",),
                
            dbc.Row([
                html.H2("Distance graph (total in km travelled): "),
                html.Div(children=dcc.Graph(id="distance-graph", config={"displayModeBar": True},)),
                ],className="card",),
                
            dbc.Row([
                html.H2("Cluster By longitude, latitude, speed and hours k=10"),
                html.Div(children=dcc.Graph(id="cluster-graph", config={"displayModeBar": True},)),
                dash_table.DataTable(id='table2_out',data=[], columns=[], page_size=7,
                style_table={'overflowX': 'auto'},
                style_cell={
                # all three widths are needed
                'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                            }),
                
                ],className="card",),
                        
    ])
    ]
    
)


@app.callback(
    
    [   Output("speed-chart", "figure"),
        Output("volume-chart", "figure"), 
        Output("speed-heat-chart", "figure"),
        Output('table1_out', 'data'),
        Output('table1_out', 'columns'),
        Output('output-date-picker-range', 'children'),
        Output("route-map", "figure"),
        Output("distance-graph", "figure"),
        Output("cluster-graph", "figure"),
        Output('table2_out', 'data'),
        Output('table2_out', 'columns'),
        Input('submit-button-state', component_property='n_clicks'),
        Input("show_tables", "value"),
        State("vehicle-filter", "value"),
        State("groupBy", "value"),
        State("date-range", "start_date"),
        State("date-range", "end_date"),
        State("speed-slider", "value")
        
        
    ],
             )
             
def update_charts(n_clicks, table_status, name, groupBy ,start_date, end_date, slider_range):
    data_display = ""
    
    if n_clicks is None:
        raise PreventUpdate
        
    else:
        
        
        # traer informacion de la BD
       
        url = "https://ds4a-api.muniter.xyz/record/"
        car_name = name+"/"
        initial_date = str(start_date)+"T00:00:00"+"/"
        final_date = str(end_date)+"T00:00:00"
        get_car = url+car_name+initial_date+final_date
        data = requests.get(get_car).json()
        record=pd.DataFrame(data)
        size = record.shape[0]

        if(groupBy=="first day"):
            mask = ( record['datetime'].str.split('T').str[0] == start_date)
            record=record[mask]
            
        #data_display=get_car
    
        if record.empty:
            # aplica si no hay informacion en el query para que las graficas esten vacias 
            
            record["date"] = ""
            record["speed"] = ""
            record["longitude"] = ""
            record["hours"] = ""
            
            full_chart_figure = blank_fig()
            day_week_graph = blank_fig()
            speed_graph = blank_fig() 
            day_week_graph = blank_fig()
            route_map = blank_fig()
            distance_graph = blank_fig()
            cluster_graph = blank_fig()
            
            table1_columns=[]
            table1_data=[]
            
            table2_columns=[]
            table2_data=[]
            
        
        else:
            record = record.sort_values(by='datetime')
            
            #separa los dias y las horas 
            record[['date', 'hours']] = record['datetime'].str.split('T', 1, expand=True)
            record["date"] = pd.to_datetime(record['date'])
            
            # actualiza el camplo a dd-mm-yyyy
            record["date"] = record["date"].dt.strftime('%d-%m-%Y')            
            #record = record.sort_values(['date', 'hours'])
            
            #para filtrar en df
            datetime_obj = datetime.strptime(start_date, '%Y-%m-%d')
            new_start_date = datetime_obj.strftime("%d-%m-%Y")

            datetime_obj2 = datetime.strptime(end_date, '%Y-%m-%d')
            new_end_date = datetime_obj2.strftime("%d-%m-%Y")    

            record['day_week'] =  pd.to_datetime(record['date'])
            record['day_week'] =  record['day_week'].dt.day_of_week
            
            record[['hora', 'minutos','segundos']]  = record['hours'].str.split(':', expand=True)
            
            record = calculate_distance(record)


            y_plot = "speed"
            size_val = "speed"
            color_val = "speed"
            
            if(groupBy=="date range"):
                df = record.copy()
                x_plot = "date"
                
            elif(groupBy=="first day"):
                
                df = record[(record['date'] == new_start_date)]
                x_plot = "hours"
                
                
            # utilizado para filtrar por velocidades
            low, high = slider_range
            mask = (df['speed'] > low) & (df['speed'] < high)
            df=df[mask]
                
            if(table_status=="yes"):
                table1_columns = [{"name": i, "id": i} for i in df.columns]
                table1_data = df.to_dict('records')
            else:
                table1_columns=[]
                table1_data=[]

#-//////////////////////////////////////////////////////////////////// Graficas//////////////////////////////////////////////////////////////                        
            full_chart_figure = create_figure_scatter(df, x_plot, y_plot, color_val)
        
            color = "#E12D39"
            title = "filtered speed and data"
            hovertemplateinfo='m/s'
            type='lines'
        
            #px.set_mapbox_access_token(open(".mapbox_token").read())
            day_week_graph  = px.scatter_mapbox(
                df, 
                lat='latitude',
                lon='longitude',
                color='day_week',
                mapbox_style='open-street-map' )
                
            zoom, center = zoom_center(lons=df.longitude, lats=df.latitude)
            day_week_graph.update_layout(
            hovermode="closest",
            mapbox_style="open-street-map",
            mapbox=dict(center=center, bearing=0, pitch=0, zoom=zoom),
            margin=dict(l=0, r=0, t=0, b=0),)
                
            speed_graph = px.density_mapbox(df, lat='latitude', lon='longitude', z='speed', radius=10,mapbox_style='open-street-map')
            #speed_graph = px.scatter_mapbox(df, lat='latitude', lon='longitude', color="speed", size="speed", mapbox_style='open-street-map', color_continuous_scale=px.colors.cyclical.IceFire,)
            
            zoom, center = zoom_center(lons=df.longitude, lats=df.latitude)
            speed_graph.update_layout(
            hovermode="closest",
            mapbox_style="open-street-map",
            mapbox=dict(center=center, bearing=0, pitch=0, zoom=zoom),
            margin=dict(l=0, r=0, t=0, b=0),)
            
            route_map = map_route(df)
            
            distance_graph = distance_traveled_figure(df)
            
            ar_work_w31 = df[['longitude','latitude','speed','hora']].to_numpy()
            
            clus = KMeans(n_clusters=10).fit(ar_work_w31).labels_
            df['k1'] =clus
            cluster_graph = px.scatter_mapbox(df, lat='latitude',lon='longitude', color='k1',zoom=5,hover_data=[df['speed'],df['hora']],)
            cluster_graph.update_layout(mapbox_style='open-street-map')
            
            zoom, center = zoom_center(lons=df.longitude, lats=df.latitude)
            cluster_graph.update_layout(
            hovermode="closest",
            mapbox_style="open-street-map",
            mapbox=dict(center=center, bearing=0, pitch=0, zoom=zoom),
            margin=dict(l=0, r=0, t=0, b=0),)
            
            df3 =df.groupby('k1').agg({'speed':['min','max','mean'],'hora':['min','max','mean'],'id':'count'})
            
            table2_columns = [{"name": i, "id": i} for i in df3.columns]
            table2_data = df3.to_dict('records')
    
        return full_chart_figure, day_week_graph, speed_graph, table1_data, table1_columns, data_display, route_map, distance_graph, cluster_graph,  [],  []

#_______________________________________________________________________________________________________________________________
def create_figure_scatter(df, x_plot, y_plot, color_val):

    fig = px.scatter(
        df, 
        x=x_plot, 
        y=y_plot, 
        #size=size_val, 
        marginal_x="histogram", 
        marginal_y="violin", 
        color=color_val
        )
    return fig

def create_figure_line(df, x_plot, y_plot, type, hovertemplateinfo, title, color):

    x_plot = df[x_plot]
    y_plot = df[y_plot]

    chart_figure = {
        "data": [{
        "x": x_plot,
        "y": y_plot,
        "type": type,
        "hovertemplate": "%{y:.2f}"+hovertemplateinfo+"<extra></extra>",
                },],
                
        "layout": {
        "title": {
        "text": title, "x": 0.05, "xanchor": "left",},
        "xaxis": {"fixedrange": True},
        "yaxis": {"tickprefix": "", "fixedrange": True},
        "colorway": [color],},}
    return chart_figure

def blank_fig():
    fig = px.scatter(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    
    return fig   
    
def map_route(data: pd.DataFrame):
    fig = go.Figure(
        data=go.Scattermapbox(
            lon=data.longitude,
            lat=data.latitude,
            mode="markers+lines",
        )
    )

    zoom, center = zoom_center(lons=data.longitude, lats=data.latitude)
    fig.update_layout(
        hovermode="closest",
        mapbox_style="open-street-map",
        mapbox=dict(center=center, bearing=0, pitch=0, zoom=zoom),
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig
    
#******************************************************************************************************************************    
def zoom_center(
    lons: tuple | None = None,
    lats: tuple | None = None,
    lonlats: tuple | None = None,
    projection: str = "mercator",
    width_to_height: float = 2.0,
) -> tuple[float, dict]:
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
       
#******************************************************************************************************************************


def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """
    slightly modified version: of http://stackoverflow.com/a/29546836/2901002
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees or in radians)
    All (lat, lon) coordinates must have numeric dtypes and be of equal length.
    """
    if to_radians:
        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)

    a = (
        np.sin((lat2 - lat1) / 2.0) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2.0) ** 2
    )

    return earth_radius * 2 * np.arcsin(np.sqrt(a))   
    
def calculate_distance(data: pd.DataFrame):
    if "distance" not in data.columns:
        data["distance"] = haversine(
            data.latitude.shift(1),
            data.longitude.shift(1),
            data.loc[1:, "latitude"],
            data.loc[1:, "longitude"],
        )
        data["cum_distance"] = data.distance.cumsum()

    return data

def distance_traveled_figure(data: pd.DataFrame):
    fig = px.line(
        x=data.datetime,
        y=data.cum_distance,
        labels={"x": "Date", "y": "Distance (km)"},
    )
    return fig
    
    
if __name__ == "__main__":
    app.run(debug=os.environ.get('ENV') != 'production')




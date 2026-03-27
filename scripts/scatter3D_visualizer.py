from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
import random
import zmq

scene = dict(
        xaxis = dict(nticks=10, range=[-1,1],),
        yaxis = dict(nticks=10, range=[-1,1],),
        zaxis = dict(nticks=10, range=[-1,1],)
        )

camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=-0.1),
        eye=dict(x=1.5, y=1.5, z=0.1)
        )

app = Dash("Skeleton tracking 3D scatter")

app.layout = html.Div([
    html.H4('Skeleton tracking 3D scatter'),
    dcc.Graph(id="graph"),
    dcc.Interval(
            id='interval-component',
            interval=500, # in milliseconds
            n_intervals=0
        )
    ], 
    id = "change-height", 
    style={'width': '100%', 'display': 'inline-block', 'height': '100%'})

@app.callback(Output("graph", "figure"), Input('interval-component', 'n_intervals'))
def update_bar_chart(n_intervals):
    x=[random.random(), random.random(), random.random()]
    y=[random.random(), random.random(), random.random()]
    z=[random.random(), random.random(), random.random()]
    fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='markers')])

    fig.update_layout(scene_aspectmode='cube', height=1200, width=1500, margin=dict(r=20, l=20, b=10, t=10))
    fig.update_layout(scene=scene, scene_camera=camera)

    return fig

app.run(debug=True)
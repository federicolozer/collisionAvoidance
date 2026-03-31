#!/usr/bin/env python3

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
import random
import zmq
import json
import time
import threading
import signal



endpoint = "tcp://localhost:6000"
topic = "SKEL"
running = True

zctx = zmq.Context.instance()
socket = zctx.socket(zmq.SUB)
socket.connect(endpoint)

# Subscribe to "news" topic (prefix match)
socket.setsockopt_string(zmq.SUBSCRIBE, "SKEL")



scene = dict(
        xaxis = dict(nticks=10, range=[-2,2],),
        yaxis = dict(nticks=10, range=[-2,2],),
        zaxis = dict(nticks=10, range=[0,2],)
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
            interval=200, # in milliseconds
            n_intervals=0
        )
    ], 
    id = "change-height", 
    style={'width': '100%', 'display': 'inline-block', 'height': '100%'})



@app.callback(Output("graph", "figure"), Input('interval-component', 'n_intervals'))
def update_bar_chart(n_intervals):
    global data

    t1 = time.time()


    x = []
    y = []
    z = []
    for [*pnt] in data:
        x.append(pnt[0])
        y.append(pnt[1])
        z.append(pnt[2])
    fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='markers')])

    t2 = time.time()
    print(f"Time elapsed for receiving data: {t2 - t1}")

    fig.update_layout(scene_aspectmode='cube', height=1200, width=1500, margin=dict(r=20, l=20, b=10, t=10))
    fig.update_layout(scene=scene, scene_camera=camera)

    t3 = time.time()
    print(f"Time elapsed for updating figure: {t3 - t2}")

    return fig



def data_receiver():
    global running, data
    while running:
        topic, message = socket.recv_string().split(" ", 1)
        array = json.loads(message)

        data = array





def main():
    # Gestione segnali per chiusura pulita (es. CTRL+C o kill da script bash)
    def signal_handler(sig, frame):
        global running
        running = False
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    

    thread = threading.Thread(target=data_receiver, args=())
    thread.start()

    print("Running")
    app.run(debug=True, port=8051)

    thread.join()



if __name__ == "__main__":
     main()
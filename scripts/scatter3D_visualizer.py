#!/usr/bin/env python3

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
import random
import zmq
import json
import signal
import threading
import time





# Parameters
endpoint = "tcp://localhost:6000"
topic = "SKEL"
running = True
scene = dict(
        xaxis = dict(nticks=10, range=[-1, 1],),
        yaxis = dict(nticks=10, range=[-1, 1],),
        zaxis = dict(nticks=10, range=[0, 2],)
        )
camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=-0.1),
        eye=dict(x=1.5, y=1.5, z=0.1)
        )

app = Dash(__name__)

data = None
socket = None






class SkeletonVisualizer:
    def __init__(self, socket):
        self.started = False
        self.socket = socket
        self.data = None
        self.mutex = threading.Lock()
        self.thread = threading.Thread(target=self.data_receiver, args=())

    def start(self):
        if self.started:
            return
        self.started = True
        self.thread.start()
        return self

    def data_receiver(self):
        global running, data
        while running:
            topic, message = self.socket.recv_string().split(" ", 1)
            array = json.loads(message)
            # print(f"Received: {array}")
            with self.mutex:
                self.data = array
                data = array


    def read_frame(self):
        with self.mutex:
            frame = self.data.copy() if self.data is not None else None
        return frame
    
    

    def load_interface(self):
        app.run(debug=True)






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



# Main loop to receive data via ZeroMQ and update the plot
def main():
    global socket
    zctx = zmq.Context.instance()
    socket = zctx.socket(zmq.SUB)
    socket.connect(endpoint)

    # Subscribe to "news" topic (prefix match)
    socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    app.layout = html.Div([
    html.H4('Skeleton tracking 3D scatter'),
    dcc.Graph(id="graph"),
    dcc.Interval(
            id='interval-component',
            interval=20, # in milliseconds
            n_intervals=0)
    ], 
    id = "change-height", 
    style={'width': '100%', 'display': 'inline-block', 'height': '100%'})

    # Gestione segnali per chiusura pulita (es. CTRL+C o kill da script bash)
    def signal_handler(sig, frame):
        global running
        running = False
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Launch data receiver thread and load the Dash interface
    vis = SkeletonVisualizer(socket).start()
    #vis.load_interface()



    print("Sta partendo")
    app.run(debug=True, port=8008)
    print("Partito")


    
    

    # socket.close()



if __name__ == "__main__":
    main()
    
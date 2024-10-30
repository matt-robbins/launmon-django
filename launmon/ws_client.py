#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:5678") as websocket:
        while True:
            message = websocket.recv()
            print(f"Received: {message}")

hello()

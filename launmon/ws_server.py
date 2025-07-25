#!/usr/bin/env python
import asyncio
import websockets
import redis
import json

CONNECTIONS = set()
r = redis.Redis()
p = r.pubsub(ignore_subscribe_messages=True)

async def register(websocket):
    CONNECTIONS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CONNECTIONS.remove(websocket)

async def rebroadcast():
    while True:
        message = p.get_message(timeout=1)
        if (message is not None):
            ch, machine = str.split(message['channel'].decode(),':')
            _, ch = str.split(ch, '-') 
            data = message['data'].decode()
            packet = {"location": machine, ch: data}

            websockets.broadcast(CONNECTIONS, json.dumps(packet))
        await asyncio.sleep(0) # give new clients a chance to register

async def main():
    async with websockets.serve(register, "localhost", 5678):
        await rebroadcast()

if __name__ == "__main__":
    p.psubscribe("launmon-status:*")
    p.psubscribe("launmon-subscriber:*")
    # p.psubscribe("launmon-current:*")
    asyncio.run(main())

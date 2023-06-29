from typing import Any

from pip._vendor import requests
import websockets
from websockets.exceptions import ConnectionClosed
import aiohttp
import asyncio
import json

all_clients = []


async def send_message(message: str):
    for client in all_clients:
        try:
            await client.send(message)
        except ConnectionClosed:
            all_clients.remove(client)


async def client_connected(client_socket, path):
    print("New client connected!")
    all_clients.append(client_socket)

    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3000/api/rest/v1/inputs/1/") as response:
                json_vmix = await response.text()
                vmix_info = json.loads(json_vmix)
                if vmix_info['media']['muted']:
                    json_answ = 'Можно разговаривать'
                else:
                    json_answ = 'Звук в эфире!'
                await send_message(json_answ)


async def start_server():
    print("Server started!")
    await websockets.serve(client_connected, "localhost", 7788)


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(start_server())
    event_loop.run_forever()

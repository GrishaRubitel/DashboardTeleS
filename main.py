from typing import Any
from pip._vendor import requests
import websockets
from websockets.exceptions import ConnectionClosed
import aiohttp
import asyncio
import json
import socket


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
    json_answ = {'air_info': True, 'message_type': 'mute_check'}

    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3000/api/rest/v1/inputs/1/") as response:
                json_vmix = await response.text()
                vmix_info = json.loads(json_vmix)
                json_answ['air_info'] = vmix_info['media']['muted']
                await send_message(json.dumps(json_answ))


class ListenerClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost):
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        print('connected')

    def data_received(self, data):
        print('Data received: {!r}'.format(data))
        json_answ = {'cam_id': data[0] - 128, 'cam_state': data[1] - 48, 'message_type': 'cameras_states'}
        asyncio.get_running_loop().create_task(send_message(json.dumps(json_answ)))

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)


async def ross_listener(host: str, port: int):
    loop = asyncio.get_running_loop()
    while True:

        on_con_lost = loop.create_future()

        transport, protocol = await loop.create_connection(
            lambda: ListenerClientProtocol(on_con_lost),
            host, port)

        try:
            await on_con_lost
        finally:
            transport.close()


async def start_listener():
    print("Listener started!")
    await ross_listener('127.0.0.1', 7355)


async def start_server():
    print("Server started!")
    await websockets.serve(client_connected, "localhost", 7788)


async def start_all(loop):
    f1 = loop.create_task(start_listener())
    f2 = loop.create_task(start_server())
    await asyncio.wait([f1, f2])


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(start_all(event_loop))
    event_loop.run_forever()

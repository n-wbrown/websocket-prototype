import asyncio
from datetime import datetime
from functools import partial

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocketDisconnect

from websockets.exceptions import ConnectionClosedError

import aiofiles
from numpy import random
import uvicorn


# Budget ngingx

def page_factory(file_name):
    async def page_async(request):
        async with aiofiles.open(file_name, mode='r') as f:
            contents = await f.read()
        return HTMLResponse(contents)
    return page_async

# data models 

class random_maker:
    def __init__(self):
        self.low  = 0.0
        self.high = 1.0

    def generate(self):
        result = random.rand() * (self.high - self.low) + self.low
        return str(result)

# utilities - these are unused 

kill_event = asyncio.Event()

def make_killable(app_func):
    def new_func(kill_event):
        print(kill_event)
        return partial(app_func, kill_event=kill_event)
    return new_func


async def shutdown_mgr(kill_event):
    async def shutdown_func():
        kill_event.set()

    return shutdown_func


async def shutdown():
    print("shutting down now")
    print("shutdown", kill_event)
    kill_event.set()

# apps

async def write_only_app(websocket):
    await websocket.accept()
    while True:
        try:
            text = await websocket.receive_text()
            print("text received:", text)
        except WebSocketDisconnect:
            print("terminating")
            return
    await websocket.close()


async def read_only_app(websocket):
    await websocket.accept()
    while True:
        ts = datetime.ctime(datetime.now())
        number = random.random()
        try:
            await websocket.send_text("{}  {}".format(ts, number))
        except ConnectionClosedError:
            print("disconnect")
            break
        
        await asyncio.sleep(3)

    await websocket.close()

        

async def plotter_app(websocket):
    # websocket = WebSocket(scope=scope, receive=receive, send=send)
    await websocket.accept()
    interval = 1
    text_waiter = asyncio.create_task(websocket.receive_text())
    time_waiter = asyncio.create_task(asyncio.sleep(interval))
    maker = random_maker()
    while True:
        finished, unfinished = await asyncio.wait(
            [time_waiter, text_waiter],
            return_when=asyncio.FIRST_COMPLETED
        )
        if text_waiter in finished:
            try:
                text = await text_waiter
            except WebSocketDisconnect:
                for x in unfinished:
                    x.cancel()
                return
            if str(text).startswith("high"):
                try:
                    maker.high = float(text[4:])
                except ValueError:
                    await websocket.send_text("bad high limit: " + text)
            if str(text).startswith("low"):
                try:
                    maker.low = float(text[3:])
                except ValueError:
                    await websocket.send_text("bad low limit: " + text)
            if str(text).startswith("cancel"):
                break
            # await websocket.send_text(text)
            text_waiter = asyncio.create_task(websocket.receive_text())
        if time_waiter in finished:
            await time_waiter
            await websocket.send_text(str(maker.generate()))
            time_waiter = asyncio.create_task(asyncio.sleep(interval))

    # wrap up and close 
    for x in unfinished:
        x.cancel()
    await websocket.send_text(
        "The websocket is now closed."
    )
    await websocket.close()





app = Starlette(
    debug=True,
    routes=[
        Route('/index', page_factory("index.html")),
        Route('/ws_tools.js', page_factory("ws_tools.js")),
        # write only
        Route('/write_only', page_factory('write_only.html')),
        WebSocketRoute('/write_only/ws', write_only_app),
        # read only
        Route('/read_only', page_factory('read_only.html')),
        Route('/read_only.js', page_factory('read_only.js')),
        WebSocketRoute('/read_only/ws', read_only_app),
        # plotter
        Route('/plotter', page_factory('plotter.html')),
        Route('/plotter.js', page_factory('plotter.js')),
        WebSocketRoute('/plotter/ws', plotter_app),

        
        Route('/home', page_factory("home.html")),
    ],
)

if __name__ == '__main__':
    uvicorn.run("starlette_backend:app", host="127.0.0.1", port=5000,
                log_level='info')

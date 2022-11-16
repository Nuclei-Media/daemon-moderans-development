from fastapi import FastAPI
import socketio


def handle_connect(sid, environ):
    print("connect ", sid)


class SocketManager:
    def __init__(self) -> None:
        self.server = socketio.AsyncServer(
            cors_allowed_origins="*",
            async_handlers=True,
            async_mode="asgi",
            logger=True,
            engineio_logger=True,
        )
        self.app = socketio.ASGIApp(self.server)

    @property
    def on(self):
        return self.server.on

    @property
    def send(self):
        return self.server.send

    def mount_to(self, path: str, app: FastAPI):
        app.mount(path, self.app)

    def send_files(self, sid, files):
        self.send(sid, files)

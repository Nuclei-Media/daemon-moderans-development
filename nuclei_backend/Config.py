import typing


class Config(object):
    OS: typing.String["windows" | "linux"] = "windows"

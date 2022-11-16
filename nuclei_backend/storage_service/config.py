import pathlib
from importlib.resources import path
from typing import Final


# It's a class that defines a bunch of constants
class Config(object):

    IPFS_CONNECT_URL: Final = "/ip4/127.0.0.1/tcp/5001/http"
    IPFS_FILE_URL: Final = "http://127.0.0.1:8080/ipfs/"
    DOMAIN: Final = "http://localhost:5000"
    # get the full path to the temp folder
    TEMP_FOLDER: Final = pathlib.Path(__file__).parent.joinpath("processing_temp")

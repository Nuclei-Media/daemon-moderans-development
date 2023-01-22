import logging
import uvicorn
import os

# import tje app from __init__.py
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting server")
    uvicorn.run("container:app", host="0.0.0.0", port=80, log_level="info")

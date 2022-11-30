import logging

import uvicorn

from nuclei_backend import app

# add logging for the app
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("nuclei_backend:app", host="0.0.0.0", reload=True)

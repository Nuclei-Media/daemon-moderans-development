import logging

from nuclei_backend import app

# add logging for the app
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run("0.0.0.0", port=5000, debug=True, threaded=True)

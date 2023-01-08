import logging

import uvicorn
import subprocess
from nuclei_backend import app

# add logging for the app


def print_ip():
    ip = (
        subprocess.check_output("ipconfig")
        .decode("utf-8")
        .split("IPv4 Address. . . . . . . . . . . : ")[1]
        .split("Subnet Mask")[0]
    )
    print(f"\nserver running on : http://{ip.strip()}:8000\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print_ip()
    uvicorn.run("nuclei_backend:app", host="0.0.0.0", reload=True)

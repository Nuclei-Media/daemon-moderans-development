import logging

import uvicorn
import subprocess
from nuclei_backend import app

# add logging for the app


def print_ip():
    # use subprocess to print out the ip address of the machine
    # strip the output of the command to get the ip address on windows
    ip = (
        subprocess.check_output("ipconfig")
        .decode("utf-8")
        .split("IPv4 Address. . . . . . . . . . . : ")[1]
        .split("Subnet Mask")[0]
    )
    print(f"\nserver running on : {ip.strip()}:8000\n")
    return ip


if __name__ == "__main__":
    # print out the ip address of the machine
    logging.basicConfig(level=logging.INFO)
    print_ip()
    uvicorn.run("nuclei_backend:app", host="0.0.0.0", reload=True)

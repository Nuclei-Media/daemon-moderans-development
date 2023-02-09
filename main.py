import logging
import subprocess
import pathlib
import uvicorn


def ip_addy():
    ip = (
        subprocess.check_output("ipconfig")
        .decode("utf-8")
        .split("IPv4 Address. . . . . . . . . . . : ")[2]
        .split("Subnet Mask")[0]
    )
    return f"\nserver runniyng on : https://{ip.strip()}:443\n"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # logging.log(1, ip_addy())
    # print(ip_addy())
    uvicorn.run("nuclei_backend:app", port=5000, reload=True, use_colors=True)

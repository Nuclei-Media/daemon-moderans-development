import subprocess


def docker_refresher():
    # get the output
    output = subprocess.check_output(
        "docker build .", shell=True, text=True, stderr=subprocess.STDOUT
    )
    print(output)
    # extract the image id
    image_id = output.split("writing image")[1].split("\n")[0]
    # remove the whitespace
    print(image_id)
    image_id = image_id.strip()
    # remove the sha256:
    print(image_id)
    image_id = image_id.split("sha256:")[1]
    # remove the whitespace
    image_id = image_id.strip()
    # remove the trailing comma
    image_id = image_id.split("done")[0]
    # remove the whitespace
    image_id = image_id.strip()
    print(image_id)

    pusher = subprocess.check_output(
        f"docker tag {image_id} ronnytec/nuclei:latest", shell=True
    )
    subprocess.call("docker push ronnytec/nuclei:latest", shell=True)


if __name__ == "__main__":
    docker_refresher()

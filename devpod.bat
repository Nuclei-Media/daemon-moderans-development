@echo off
podman pod create --name mypod

podman container create --name postgres \
    -e POSTGRES_PASSWORD=postgrespw \
    -p 5432:5432 \
    -v data:/var/lib/postgresql \
    postgres:latest
podman container start postgres

podman container create --name redis-server \
    -p 6379:6379 \
    redis:latest
podman container start redis-server

podman container create --name ipfs \
    --privileged \
    --cap-add SYS_ADMIN \
    --security-opt apparmor:unconfined \
    --device /dev/fuse \
    -e IPFS_PROFILE=server \
    -e IPFS_PATH=/ipfsdata \
    -p 8080:8080 \
    -p 4001:4001 \
    -p 5001:5001 \
    -v ./data/ip

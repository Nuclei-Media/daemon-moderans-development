import base64

import httpx
from fastapi import Depends, File, HTTPException, UploadFile, status
from tqdm import tqdm

from nuclei_backend.users.auth_utils import get_current_user

from ...users.user_handler_utils import get_db
from ..ipfs_utils import *
from ..main import storage_service
from .video_compression_utils import CompressVideo, cleanup_file, save_to_temp

# https://stackoverflow.com/questions/70043665/fastapi-unvicorn-request-hanging-during-invocation-of-call-next-path-operation


@storage_service.post("/compress/video")
async def compress_task(
    files: List[UploadFile],
    rate: str = "lossless",
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):
    for file in files:
        _file = file.file
        _file = _file.read()

        if identity_token is None:
            return {"message": "Unauthorised user"}, status.HTTP_401_UNAUTHORIZED
        if not file:
            return {"error": "No file uploaded"}
        try:
            temp_dir = save_to_temp(_file)

        except Exception as e:
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST
        if temp_dir is None:
            return {
                "error": "Could not save file to temporary location"
            }, status.HTTP_400_BAD_REQUEST
        compressing_video = CompressVideo(rate, temp_dir)
        compressed_video = compressing_video.produce_compression()
        if ipfs_flag:
            compressing_video.commit_to_ipfs(
                compressed_video, file.filename, identity_token, db
            )
    return {"message": "Successfully compressed video"}, status.HTTP_200_OK

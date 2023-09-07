from concurrent.futures import ThreadPoolExecutor
import time
from typing import List
import httpx
from fastapi import BackgroundTasks, Depends, HTTPException, UploadFile, status

from nuclei_backend.database import SessionLocal

from ...users.auth_utils import get_current_user
from ...users.user_handler_utils import get_db
from ..main import storage_service
from .image_compression_utils import CompressImage
import logging
from ...user_quota.quota_utils import get_current_quota, increase_quota


def process_file(
    file: bytes, filename: str, ipfs_flag: bool, identity_token: str, db
) -> None:
    try:
        compressing_file = CompressImage(file, filename)

        print("files compressed")
        compressed_file = compressing_file.produce_compression()
        if ipfs_flag:
            print("before ipfs flag")
            try:
                with db as _db:
                    compressing_file.commit_to_ipfs(
                        compressed_file, filename, identity_token, _db
                    )
            except Exception as e:
                print(f"the error was {e}")
        compressing_file.cleanup_compression_outcome()
    except Exception as e:
        print(f"Error compressing and storing file {filename}: {str(e)}")


def process_files(
    files: List[UploadFile],
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):
    logging.debug("before thread pool executor")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for file in files:
            _filename = file.filename.replace(" ", "_")
            _file = file.file.read()  # Read the file contents as bytes
            future = executor.submit(
                process_file, _file, _filename, ipfs_flag, identity_token, db
            )
            futures.append(future)

        results = [future.result() for future in futures]

    return results


@storage_service.post("/compress/image")
async def compress_task_image(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    ipfs_flag: bool | None = True,
    identity_token: str = Depends(get_current_user),
    db=Depends(get_db),
):
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded",
        )

    try:
        # Send the task to the background
        background_tasks.add_task(process_files, files, ipfs_flag, identity_token, db)
        # Prepare the data to be sent to the /data/quota/increase endpoint
        increase_amount = sum([len(file.file.read()) for file in files])
        files_count = len(files)

        try:
            # Call the increase_quota function using the new_db connection
            current_byte_amount = get_current_quota(identity_token.id, db).user_quota
            if (current_byte_amount + increase_amount) == current_byte_amount:
                raise HTTPException(status_code=401, detail="Quota amount mismatch")

            increase_quota(identity_token.id, db, increase_amount, files_count)
            db.commit()
            # Return
            return {"message": "Increased"}, 200
        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error in compress_task_image: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error in compress_task_image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

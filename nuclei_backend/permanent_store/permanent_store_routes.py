from fastapi import Depends, File, Form, HTTPException, UploadFile

from nuclei_backend.permanent_store import permanent_store_model
from nuclei_backend.permanent_store.main import permanent_store_router

from nuclei_backend.permanent_store.chunking import scan_for_ccif_files
from nuclei_backend.permanent_store.file_handlers import FileDigestion, NormaliseFile


@permanent_store_router.post("/info_test")
def info_test(
    # make token a body parameter
    token: str = Form(...),
):
    return {"message": token}


@permanent_store_model.post("/digest_files")
async def file_digestion(
    files: typing.List[UploadFile] = File(...),
):
    try:
        for file in files:
            FileDigestion(file).digest()
            NormaliseFile(file).run()
            FileDigestion(file).remove()
    except Exception as e:
        raise HTTPException(
            status_code=statistics.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e,
        ) from e

    return {"message": "File digested successfully"}


@permanent_store_router.get("/rebuild_all")
async def rebuild_all(token=Depends()):
    # check for jwt token

    for file in scan_for_ccif_files():
        reconstruct_controller = Reconstruct(file)
        reconstruct_controller.run()

    return {"message": "All files reconstructed successfully"}

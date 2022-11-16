import logging

from fastapi import Depends, HTTPException

from ..storage_service.ipfs_model import DataRecord


def get_user_cids(user_id, db) -> list:
    """
    It returns a list of all the DataRecord objects that have the same owner_id as the user_id passed in

    Arguments:

    * `user_id`: the user's id
    * `db`: SQLAlchemy database object

    Returns:

    A list of DataRecord objects
    """

    try:
        return db.query(DataRecord).filter(DataRecord.owner_id == user_id).all()
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_collective_bytes(user_id: int, db: Session) -> int:
    """
    It takes a user_id and a database session as input, and returns the sum of the file_size of all the
    DataRecords that have the same owner_id as the user_id

    Arguments:

    * `user_id`: int
    * `db`: Session = Depends(get_db)

    Returns:

    The sum of the file_size of all the records that belong to the user_id
    """

    try:
        query = db.query(DataRecord).filter(DataRecord.owner_id == user_id).all()
        return sum(record.file_size for record in query)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def paginate_using_gb(
    user_id: int, db: Session, page_size: int = 10, page: int = 1
) -> list:
    """
    It takes a user_id, a database connection, a page_size, and a page number, and returns a list of
    DataRecord objects that are owned by the user_id, and whose total file size is less than the
    page_size, or a subset of those objects whose total file size is greater than the page_size.

    Arguments:

    * `user_id`: int, db: Session, page_size: int = 10, page: int = 1
    * `db`: Session = Depends(get_db)
    * `page_size`: The number of bytes to return per page
    * `page`: The page number to return.

    Returns:

    A list of DataRecord objects
    """

    try:
        query = db.query(DataRecord).filter(DataRecord.owner_id == user_id).all()
        total_bytes = sum(record.file_size for record in query)
        if total_bytes < page_size:
            return query
        else:
            return query[page_size * (page - 1) : page_size * page]
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e

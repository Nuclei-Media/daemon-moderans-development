import json
import secrets
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from functools import total_ordering, lru_cache
from fastapi.testclient import TestClient


class Nuclei(FastAPI):
    def __init__(
        self,
        *,
        title: str = "Nuclei",
        description: str = "Nuclei API",
        version: str = "0.1.0",
    ):
        super().__init__(title=title, description=description, version=version)
        self.client = TestClient(self)
        self.add_models()
        self.add_routes()
        self.configure_middlware()
        # self.tests()

    @lru_cache(maxsize=None)
    def configure_middlware(self):
        """
        It adds a middleware to the app
        """

        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.add_middleware(SessionMiddleware, secret_key="hello world x0532")

    @lru_cache(maxsize=None)
    def add_routes(self):
        """
        It's a function that adds routes to the app
        """

        from nuclei_backend.users.main import users_router
        from nuclei_backend.storage_service.main import storage_service

        from nuclei_backend.syncing_service.sync_service_main import sync_router

        # from nuclei_backend.chat_service.main import chat_controller

        # from nuclei_backend.permanent_store.main import permanent_store_router
        # from nuclei_backend.subscription_service.main import subscription_service
        # self.include_router(subscription_service)
        # self.include_router(permanent_store_router)

        self.include_router(storage_service)
        # self.include_router(chat_controller)
        self.include_router(users_router)
        self.include_router(sync_router)

    @lru_cache(maxsize=None)
    def add_models(self):
        """
        It creates the tables in the database.
        """

        from .database import SessionLocal, engine
        from .storage_service import ipfs_model
        from .users import user_models

        # from .permanent_store import permanent_store_model
        # from .chat_service import chat_model

        # from .user_quota import quota_models
        # from .subscription_service import subscription_model
        # from .meta_data_extraction import meta_data_model

        user_models.Base.metadata.create_all(bind=engine)
        # chat_model.Base.metadata.create_all(bind=engine)

        # subscription_model.Base.metadata.create_all(bind=engine)
        # meta_data_model.Base.metadata.create_all(bind=engine)

        ipfs_model.Base.metadata.create_all(bind=engine)
        # permanent_store_model.Base.metadata.create_all(bind=engine)
        # quota_models.Base.metadata.create_all(bind=engine)

    def tests(self):
        from .tests.test_users import UsersTests

        # from .tests.upload_tests import UploadTests

        UsersTests(self.client)
        # UploadTests(self.client)


app = Nuclei()

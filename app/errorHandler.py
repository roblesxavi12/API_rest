from pymongo.errors import PyMongoError
from fastapi import HTTPException
from app.exceptions import DbConnException

class ErrorHandler:
    def __init__(self):
        pass

    def handle_pymongo_error(self, error: PyMongoError):
        print("PyMongoError")
        pass

    def handle_fastapi_error(self, error: HTTPException):
        print("FastAPI Error")
        pass

    def handle_dbconn_error(self, error: DbConnException):
        print("DbConn error")
        pass

    def handle_general_error(self, error: Exception):
        print("General error")
        pass
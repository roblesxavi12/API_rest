from fastapi.responses import JSONResponse
from pymongo.errors import * # ta feo
from fastapi import HTTPException
from app.exceptions import DbConnException

class ErrorHandler:
    def __init__(self, msg):
        self.msg = msg
    
    @staticmethod
    def handle_pymongo_error(error: PyMongoError) -> dict[str, str]:
        msg = "PyMongoError"
        print(f"Error: {str(error.__class__.__name__)}")
        if isinstance(error, AutoReconnect):
            return {error.__class__.__name__: "Connection lost after 5 reconnection attempts."}
        elif isinstance(error, BulkWriteError):
            pass
        elif isinstance(error, ClientBulkWriteException):
            pass
        elif isinstance(error, ConfigurationError):
            pass
        elif isinstance(error, ConnectionFailure):
            pass
        elif isinstance(error, CursorNotFound):
            pass
        elif isinstance(error, DocumentTooLarge):
            pass
        elif isinstance(error, DuplicateKeyError):
            pass
        elif isinstance(error, EncryptedCollectionError):
            pass
        elif isinstance(error, EncryptionError):
            pass
        elif isinstance(error, ExecutionTimeout):
            pass
        elif isinstance(error, InvalidOperation):
            pass
        elif isinstance(error, InvalidName):
            pass
        elif isinstance(error, InvalidURI):
            pass
        elif isinstance(error, NetworkTimeout):
            pass
        elif isinstance(error, NotPrimaryError):
            pass
        elif isinstance(error, OperationFailure):
            pass
        elif isinstance(error, ProtocolError):
            pass
        elif isinstance(error, ServerSelectionTimeoutError):
            pass
        elif isinstance(error, WTimeoutError):
            pass
        elif isinstance(error, WaitQueueTimeoutError):
            pass
        elif isinstance(error, WriteConcernError):
            pass
        elif isinstance(error, WriteError):
            pass
        else:
            # not a PyMongoError
            pass
        if str(error) == "ConnectionFailure":
            return {"connection error": "connection attempted but failed"}
        return {"unhandled":f"function {msg}"}

    @staticmethod
    def handle_fastapi_error(error: HTTPException) -> dict[str, str]:
        msg = "\nFastAPI error\n"
        print(msg)
        return {"unhandled":f"function {msg}"}

    @staticmethod
    def handle_dbconn_error(error: DbConnException) -> dict[str, str]:
        msg = "handle_DbConn_error"
        print(msg)
        print(f"Dentro de handle_dbconn_error(): {str(error.__class__.__name__)}")
        if str(error).__class__.__name__ == "ConnectionFailure":
            return {"connection error": "connection attempted but failed"}
        return {"unhandled":f"function {msg}"}

    @staticmethod
    def handle_general_error(error: Exception):
        msg = "\nGeneral Error\n"
        print(msg)
        return JSONResponse(content={"unhandled":f"function {msg}"})

    @staticmethod
    def pymongo_autoreconnect_error(error: AutoReconnect):
        return isinstance(error, AutoReconnect)
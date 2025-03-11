from fastapi.responses import JSONResponse
from pymongo.errors import * # ta feo
from fastapi import HTTPException, status
from app.exceptions import DbConnException

class ErrorHandler:
    def __init__(self, msg):
        self.msg = msg
    
    @staticmethod
    def handle_pymongo_error(error: PyMongoError) -> dict[str, str]:
        msg = "PyMongoError"
        print(f"Error: {str(error.__class__.__name__)}")
        if isinstance(error, AutoReconnect):
            # Error handling -> Included retry decorator on mongodb functions
            return {error.__class__.__name__: "Connection lost after 5 reconnection attempts."}
        elif isinstance(error, BulkWriteError):
            return {error.__class__.__name__: "Error performing a bulk write"}
        elif isinstance(error, ClientBulkWriteException):
            return {error.__class__.__name__: "Client error performing a bulk write"}
        elif isinstance(error, ConfigurationError):
            return {error.__class__.__name__: "Something is incorrectly configured"}
        elif isinstance(error, ConnectionFailure):
            # La funcion connect() de la clase DbConn tiene el decorador retry
            return {error.__class__.__name__: "Connection to database failed or lost"}
        elif isinstance(error, CursorNotFound):
            return {error.__class__.__name__: "Cursor invalidated by  the server"}
        elif isinstance(error, DocumentTooLarge):
            return {error.__class__.__name__: "Document is too large for specified server"}
        elif isinstance(error, DuplicateKeyError):
            return {error.__class__.__name__: "insert or update failed due a duplicate key"}
        elif isinstance(error, EncryptedCollectionError):
            return {error.__class__.__name__: "The creation of some collection with encrypted_fields failed "}
        elif isinstance(error, EncryptionError):
            return {error.__class__.__name__: f"Error caused by: {error.cause}"}
        elif isinstance(error, ExecutionTimeout):
            return {error.__class__.__name__: "Query exceeded specified maximum query time"}
        elif isinstance(error, InvalidOperation):
            return {error.__class__.__name__: "Invalid Operation"}
        elif isinstance(error, InvalidName):
            return {error.__class__.__name__: "Invalid name"}
        elif isinstance(error, InvalidURI):
            return {error.__class__.__name__: "Tried to parse an invalid URI"}
        elif isinstance(error, NetworkTimeout):
            return {error.__class__.__name__: "Socket exceeded the specified maximum network time"}
        elif isinstance(error, NotPrimaryError):
            # handled on client side
            return {error.__class__.__name__: "The queried node is not primary or is it recovering"}
        elif isinstance(error, OperationFailure):
            return {error.__class__.__name__: "Operation failed"}
        elif isinstance(error, ProtocolError):
            return {error.__class__.__name__: "wire protocol error"}
        elif isinstance(error, ServerSelectionTimeoutError):
            return {error.__class__.__name__: "No server is available for this operation" if error.timeout == False else "Error caused by server selection timeout"}
        elif isinstance(error, WTimeoutError):
            return {error.__class__.__name__: "Operation time exceeded"}
        elif isinstance(error, WaitQueueTimeoutError):
            return {error.__class__.__name__: "Wait queue timeout error"}
        elif isinstance(error, CollectionInvalid):
            return {error.__class__.__name__: "Collection Validation Failed"}
        # elif isinstance(error, WriteConcernError):
            # pass
        # elif isinstance(error, WriteError):
            # pass
        else:
            return {error.__class__.__name__: "Not a PyMongo error. I dunno how we got here :("}

    @staticmethod
    def handle_fastapi_error(error: HTTPException) -> dict[str, str]:
        if error.status_code == status.HTTP_404_NOT_FOUND:
            return {'Error 404': 'Document not found'}
        else:
            return {"unknown error": "dunno how we got here :("}

    @staticmethod
    def handle_dbconn_error(error: DbConnException) -> dict[str, str]:
        msg = "handle_DbConn_error"
        print(msg)
        print(f"Dentro de handle_dbconn_error(): {str(error.__class__.__name__)}")
        if str(error).__class__.__name__ == "ConnectionFailure":
            return {"connection error": "connection attempted but failed"}
        return {"unhandled":f"function {msg}"}

    @staticmethod
    def handle_general_error(error: Exception) -> dict[str, str]:
        msg = "\nGeneral Error\n"
        print(msg)
        return {"unhandled":f"function {msg}"}

    @staticmethod
    def pymongo_autoreconnect_error(error: AutoReconnect):
        return isinstance(error, AutoReconnect)
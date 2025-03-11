from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, HTTPException
from pydantic_core.core_schema import ErrorType
from app.databaseConn import DbConn
from app.errorHandler import ErrorHandler
from pymongo.errors import PyMongoError

router = APIRouter()

@router.get(
    "/theaters/",
    response_description="get all theaters",
    status_code=status.HTTP_200_OK)
async def get_all() -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('theaters')
        code, msg = conn.query({})

        return JSONResponse(content=msg)
    except PyMongoError as e:
        errorMsg = ErrorHandler.handle_pymongo_error(e)
        return JSONResponse(errorMsg)
    except Exception as e:
        errorMsg = ErrorHandler.handle_general_error(e)
        return JSONResponse(errorMsg)

@router.get(
    "/theaters/{theaterId}",
    response_description="get theater by id",
    status_code=status.HTTP_200_OK)
async def get_theater_by_id(theaterId: int) -> JSONResponse:
    try:
        conn=DbConn('sample_mflix')
        code, msg = conn.connect('theaters')
        if not conn.exists({'theaterId': theaterId}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"teatro con id: {theaterId} no encontrado")

        code, msg = conn.query({'theaterId': theaterId})
        return JSONResponse(content=msg)
    except PyMongoError as e:
        errorMsg = ErrorHandler.handle_pymongo_error(e)
        return JSONResponse(content=errorMsg)
    except HTTPException as e:
        errorMsg = ErrorHandler.handle_fastapi_error(e)
        return JSONResponse(content=errorMsg)
    except Exception as e:
        errorMsg = ErrorHandler.handle_general_error(e)
        return JSONResponse(content=errorMsg)
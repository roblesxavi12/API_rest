from os import error
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, HTTPException
from pydantic_core.core_schema import ErrorType
from app.databaseConn import DbConn
from app.errorHandler import ErrorHandler
from pymongo.errors import PyMongoError

router = APIRouter()

@router.get(
    "/movies/",
    response_description="get all movies", 
    status_code=status.HTTP_200_OK)
async def get_all_movies() -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('movies')
        code, msg = conn.query({})

        return JSONResponse(content=msg)
    except PyMongoError as e:
        errorMsg = ErrorHandler.handle_pymongo_error(e)
        print(errorMsg)
        return JSONResponse(content=errorMsg)
    except Exception as e:
        print(str(e))
        errorMsg = ErrorHandler.handle_general_error(e)
        print("---get_all_movies()---",errorMsg)
        return JSONResponse(content=errorMsg)

@router.get(
    "/movies/{genre:str}",
    response_description="get movie by genre",
    status_code=status.HTTP_200_OK)
async def get_movie_by_genre(genre: str):
    try:
        conn = DbConn('sample_mflix')
        code,msg = conn.connect('movies')
        if not conn.exists({"genres":{"$in":[genre]}}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"peliculas con el genero {genre} no encontradas")
        code,msg = conn.query({"genres":{"$in":[genre]}})
        return JSONResponse(content=msg)
    except PyMongoError as e:
        pass
    except HTTPException as e:
        pass
    except Exception as e:
        pass

from os import error
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, HTTPException, Query
from pydantic_core.core_schema import ErrorType
from app.databaseConn import DbConn
from app.errorHandler import ErrorHandler
from pymongo.errors import PyMongoError
from typing import Union

router = APIRouter()

@router.get(
    "/movies/",
    response_description="get all movies", 
    status_code=status.HTTP_200_OK)
async def get_all_movies(lim: int=50) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('movies')
        code, msg = conn.query({}, lim)

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
    "/movies/genre/{genre:str}",
    response_description="get movie by genre",
    status_code=status.HTTP_200_OK)
async def get_movie_by_genre(genre: str, lim: int=10): 
    try:
        conn = DbConn('sample_mflix')
        code,msg = conn.connect('movies')
        if not conn.exists({"genres":{"$in":[genre]}}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"peliculas con el genero {genre} no encontradas")
        code,msg = conn.query({"genres":{"$in":[genre]}}, lim)
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

@router.get(
    "/movies/year/{year:int}",
    response_description="get movies by year",
    status_code=status.HTTP_200_OK)
async def get_movies_by_year(year: int, lim: int=5) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('movies')
        if not conn.exists({"year":year}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"peliculas del año {year} no encontradas")
        
        code, msg = conn.query({"year": year}, lim)
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

@router.get(
    "/movies/lang/{lang:str}",
    response_description="get movies by language",
    status_code=status.HTTP_200_OK)
async def get_movies_by_lang(lang: str, lim: int=5) -> JSONResponse:
    try:
        conn = DbConn("sample_mflix")
        code, msg = conn.connect('movies')
        if not conn.exists({"languages": {"$in":[lang]}}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"peliculas con el idioma {lang} no encontradas")

        code, msg = conn.query({"languages": {"$in":[lang]}},lim)
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

@router.get(
    "/movies/{movieId: str}",
    response_description="get movies by its unique id",
    status_code=status.HTTP_200_OK)
async def get_movies_by_id(movieId: str) -> JSONResponse:
    try:
        conn = DbConn("movies_mflix")
        code, msg = conn.connect("movies")

        if not conn.exists({"_id": ObjectId(movieId)}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"peliculas con el id {movieId} no encontradas")
        
        code, msg = conn.query({"_id":ObjectId(movieId)})
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

@router.patch(
    "/movies/",
    response_description="update movie by id(?)",
    status_code=status.HTTP_200_OK)
async def modify_movies(movie):
    pass
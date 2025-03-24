from datetime import datetime
from os import error, stat
from pydantic import BaseModel
from bson.objectid import ObjectId
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, HTTPException, Query
from pydantic_core.core_schema import ErrorType
from app.databaseConn import DbConn
from app.errorHandler import ErrorHandler
from pymongo.errors import PyMongoError
from typing import Union
"""
viewer y critic son la misma clase
seguramente usando una instancia de una de ellas ya esta bien
"""

# Post classes
class viewer(BaseModel):
    rating: float
    numReviews: int
    meter: int

class critic(BaseModel):
    rating: float
    numReviews: int
    meter: int

class tomatoes(BaseModel):
    rt_viewer: viewer
    rt_fresh: int
    rt_critic: critic
    rt_rotten: int
    rt_lastupdated: datetime

class imdb(BaseModel):
    rating: float
    votes: int
    imdb_id: int

class Movie(BaseModel):
    plot: str
    genres: list
    runtime: int
    cast: list
    poster: str
    title: str
    fullplot: str
    languages: list
    released: datetime #time -> look for exact types
    director: str
    rated: str
    awards: list
    lastupdated: datetime
    year: int
    m_imdb : imdb
    countries: list
    m_type: str
    m_tomatoes: tomatoes
    comments: str

class ModMovie(BaseModel):
    title: str
    pass

# Put classes

"""
TEST JSON
[
  {
    "_id": "573a1390f29313caabcd42e8",
    "plot": "A group of bandits stage a brazen train hold-up, only to find a determined posse hot on their heels.",
    "genres": [
      "Short",
      "Western"
    ],
    "runtime": 11,
    "cast": [
      "A.C. Abadie",
      "Gilbert M. 'Broncho Billy' Anderson",
      "George Barnes",
      "Justus D. Barnes"
    ],
    "poster": "https://m.media-amazon.com/images/M/MV5BMTU3NjE5NzYtYTYyNS00MDVmLWIwYjgtMmYwYWIxZDYyNzU2XkEyXkFqcGdeQXVyNzQzNzQxNzI@._V1_SY1000_SX677_AL_.jpg",
    "title": "The Great Train Robbery",
    "fullplot": "Among the earliest existing films in American cinema - notable as the first film that presented a narrative story to tell - it depicts a group of cowboy outlaws who hold up a train and rob the passengers. They are then pursued by a Sheriff's posse. Several scenes have color included - all hand tinted.",
    "languages": [
      "English"
    ],
    "released": "1903-12-01T00:00:00",
    "directors": [
      "Edwin S. Porter"
    ],
    "rated": "TV-G",
    "awards": {
      "wins": 1,
      "nominations": 0,
      "text": "1 win."
    },
    "lastupdated": "2015-08-13 00:27:59.177000000",
    "year": 1903,
    "imdb": {
      "rating": 7.4,
      "votes": 9847,
      "id": 439
    },
    "countries": [
      "USA"
    ],
    "type": "movie",
    "tomatoes": {
      "viewer": {
        "rating": 3.7,
        "numReviews": 2559,
        "meter": 75
      },
      "fresh": 6,
      "critic": {
        "rating": 7.6,
        "numReviews": 6,
        "meter": 100
      },
      "rotten": 0,
      "lastUpdated": "2015-08-08T19:16:10"
    },
    "num_mflix_comments": 0
  }
]
"""

router = APIRouter()

@router.get(
    "/movies/",
    response_description="get all movies", 
    status_code=status.HTTP_200_OK)
async def get_all_movies(lim: int=50) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('movies')
        code, msg = await conn.query({}, lim)

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
async def modify_movies(movie: ModMovie) -> JSONResponse:
    try:
        conn = DbConn("sample_mflix")
        code, msg = conn.connect('movies')

        if not await conn.exists({"title": movie.title}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"peliculas con el titulo {movie.title} no encontradas")
        
        mod_dict = movie.model_dump(exclude_unset=True)

        code, msg = conn.update(query_dict={"title": movie.title}, modify_dict=mod_dict)
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

@router.post(
    "/movies/",
    response_description="insert a new movie",
    status_code=status.HTTP_201_CREATED)
async def insert_movie(movie: Movie) -> JSONResponse:
    try: 
        return JSONResponse(content={})
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

@router.delete(
    "/movies/",
    response_description="delete a movie",
    status_code=status.HTTP_200_OK)
async def delete_movie(title: str) -> JSONResponse:
    try:
        conn = DbConn("sample_mflix")

        code, msg = conn.connect('movies')

        if not conn.exists({'title': title}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se ha encontrado un usuario con el email {title}")
        code, msg = conn.delete({'title':title})

        return JSONResponse(content=msg)

        return JSONResponse(content={})
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))
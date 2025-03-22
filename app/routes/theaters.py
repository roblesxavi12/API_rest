from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from fastapi import APIRouter, status, HTTPException
from pydantic_core.core_schema import ErrorType
from app.databaseConn import DbConn
from app.errorHandler import ErrorHandler
from pymongo.errors import PyMongoError
from pydantic import BaseModel
from typing import Union
router = APIRouter()

# post classes
class Address(BaseModel):
    street: str
    city: str
    state: str
    zipcode: str # Estaria guapo que fuese int

class Geolocation(BaseModel):
    gtype: str
    coordinates: list

class Location(BaseModel):
    addr: Address
    geo: Geolocation

class Theater(BaseModel):
    theaterId: int
    loc: Location

# put classes
# la idea es hacer no obligatorios el resto de entradas.
# se ha de comprobar que no sean todos None,
# es decir que no solo se envie el theaterId
class ModAddress(BaseModel):
    street: Union[None, str]
    city: Union[None, str]
    state: Union[None, str]
    zipcode: Union[None, str]

class ModGeo(BaseModel):
    gtype: Union[None, str]
    coordinates: Union[None, list]

class ModLoc(BaseModel):
    addr: ModAddress
    geo: ModGeo

class ModTheater(BaseModel):
    theaterId: int
    loc: ModLoc

@router.get(
    "/theaters/",
    response_description="get all theaters",
    status_code=status.HTTP_200_OK)
async def get_all(lim: int=50) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('theaters')
        
        code, msg = conn.query({}, lim)

        return JSONResponse(content=msg)
    except PyMongoError as e:
        errorMsg = ErrorHandler.handle_pymongo_error(e)
        return JSONResponse(errorMsg)
    except Exception as e:
        errorMsg = ErrorHandler.handle_general_error(e)
        return JSONResponse(errorMsg)

@router.get(
    "/theaters/{theaterId:int}",
    response_description="get theater by id",
    status_code=status.HTTP_200_OK)
async def get_theater_by_theaterid(theaterId: int) -> JSONResponse:
    try:
        conn=DbConn('sample_mflix')
        code, msg = conn.connect('theaters')
        if not conn.exists({'theaterId': theaterId}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"teatro con id: {theaterId} no encontrado")

        # el id no es unico (theaterId) pero deberia estar declarado como tal en la coleccion
        code, msg = conn.query({'theaterId': theaterId},1)
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

@router.get(
    "/theaters/{city_name:str}",
    response_description="get theaters by city name",
    status_code=status.HTTP_200_OK)
async def get_theater_by_city(city_name: str, lim: int=10) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('theaters')

        if not conn.exists({"location.address.city":city_name}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ciudad {city_name} no encontrada")
        code, msg = conn.query({"location.address.city":city_name},lim)
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

@router.get(
    "/theater/{theater_id:str}/",
    response_description="get theater by its unique id (ObjectID)",
    status_code=status.HTTP_200_OK)
async def get_theater_by_id(theater_id: str) -> JSONResponse:
    try:
        conn = DbConn("sample_mlfix")
        code, msg = conn.connect('theaters')

        if not conn.exists({"_id": ObjectId(theater_id)}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"teatro {theater_id} no encontrado")
        
        code, msg = conn.query({"_id": ObjectId(theater_id)})
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

@router.post(
    "/theaters/",
    response_description="add new theater",
    response_model=dict,
    status_code=status.HTTP_201_CREATED)
async def insert_theater(theater: Theater) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('theaters')

        if conn.exists({'theaterId': theater.theaterId}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"El teatro con id {theater.theaterId} ya existe")
        
        # Coordinates huele peste
        new_theater = {
            'theaterid': theater.theaterId,
            'location':{
                'address':{
                    'street': theater.loc.addr.street,
                    'city': theater.loc.addr.city,
                    'state': theater.loc.addr.state,
                    'zipcode': theater.loc.addr.zipcode
                },
                'geo':{
                    'type': theater.loc.geo.gtype,
                    'coordinates':{
                        '0':theater.loc.geo.coordinates[0],
                        '1': theater.loc.geo.coordinates[1]
                    }
                }
            }
        }

        code, result = conn.insert(data_dict=new_theater)

        return JSONResponse(content=result)
    except PyMongoError as e:
        return JSONResponse(content={})
    except HTTPException as e:
        return JSONResponse(content={})
    except Exception as e:
        return JSONResponse(content={})
"""
sample JSON for inserting
{
    "_id":"59a47286cfa9a3a73e51e734",
    "theaterId":1009,
    "location":
        {
        "address":
            {
            "street1":"6310 E Pacific Coast Hwy",
            "city":"Long Beach",
            "state":"CA",
            "zipcode":"90803"
            },
        "geo":
            {
            "type":"Point",
            "coordinates":[-118.11414,33.760353]
            }
        }
}
"""
"""SE HA DE PROBAR"""
@router.patch(
    "/theaters/",
    response_description="update theater by id",
    status_code=status.HTTP_200_OK)
async def modify_theater(theater: ModTheater) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, result = conn.connect('theaters')

        if not conn.exists({'theaterId': theater.theaterId}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El teatro con id {theater.theaterId} no existe")

        mod_dict = theater.model_dump(exclude_unset=True)

        code, msg = conn.update(query_dict={'theaterId': theater.theaterId}, modify_dict=mod_dict)
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))

# delete theater by ObjectId
"""SE HA DE PROABAR"""
@router.delete(
    "/theaters/{oid: str}",
    response_description="delete theater by ObjectId",
    status_code=status.HTTP_200_OK)
async def delete_theater_by_id(oid: str) -> JSONResponse:
    try:
        conn = DbConn("sample_mflix")
        code, msg = conn.connect('theaters')

        if not conn.exists({"_id": ObjectId(oid)}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El usuario con id {oid} no se encuentra en la base de datos")

        code, msg = conn.delete(query_dict={"_id": ObjectId(oid)})
        return JSONResponse(content=msg)
    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(e))
    except HTTPException as e:
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(e))
    except Exception as e:
        return JSONResponse(content=ErrorHandler.handle_general_error(e))
from bson import objectid
from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, status
from pydantic_core import ErrorTypeInfo
from pymongo.errors import PyMongoError, OperationFailure
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from app.databaseConn import DbConn
from app.exceptions import DbConnException
from app.errorHandler import ErrorHandler
from typing import Union
import json
import bcrypt

# https://www.datacamp.com/blog/mongodb-certification?dc_referrer=https%3A%2F%2Fwww.google.com%2F
# Se busca en la bd segun el email, lo ideal seria hacerlo con el ObjectId

# [{"name":"Miguel Martinez Gutierrez","email":"miguelitomiguelon@grefusa.com","password":"$2b$12$RncQqGHtEBpgJg8vMKh9aed7lyaE11VXAN7r8sTIPjxq4I4.0HP5m"}]

class User(BaseModel):
    name: str
    email: EmailStr
    password: str

class PostUser(BaseModel):
    name: Union[str, None] = None
    email: EmailStr
    password: Union[str, None] = None

class UserCollection(BaseModel):
    users: list[User]

class PostUserCollection(BaseModel):
    users: list[PostUser]

router = APIRouter()

# Lista completa de usuarios 
@router.get(
    "/users/",
    response_description="get all users",
    status_code=status.HTTP_200_OK)
async def get_all() -> JSONResponse:
    try:
        """
        Si los errores de DbConn se gestionan como se estan gestionando ahora, siempre van a devolver un ValueError()
        No se puede depender del 'if code == 1...' porque siempre lleva al mismo tipo de error y luego el except no 
        captura los errores propios de PyMongo
        """
        conn = DbConn('sample_mflix')

        code, msg = conn.connect('users')
        # el control de errores debe ser invisible desde aqui
        # if code == 1:
            # raise DbConnException(message=msg, error_code=code)
            # raise ValueError(msg)

        # code, msg = conn.query({"name": {"$regex": "^N"}}) # devuelve todas las entradas que el nombre empiece por N
        # el control de errores debe ser invisible desde aqui
        code, msg = conn.query({})

        # if code == 1:
            # raise DbConnException(message=msg, error_code=code)
            # raise ValueError(msg)
        
        print("before jsonresponse get all")
        return JSONResponse(content=msg)

    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(error=e))

    except Exception as e:
        # print(f"\n---serve_data() error---\n{e}\ntipo del error: {type(e).__name__}")
        # return JSONResponse(content=ErrorHandler.handle_general_error(error=e))
        print("tusmuertoss")
        return JSONResponse(content={'test':e.__class__.__name__})

# crear un nuevo usuario
@router.post(
    "/users/",
    response_description="add new user",
    response_model=dict,
    status_code=status.HTTP_201_CREATED)
async def create_user(user: User) -> JSONResponse:
    """
    test one:
    curl -X POST "http://127.0.0.1:8000/api/users/" -H "Content-Type: application/json" -d '{"name": "Miguel Gutierrez Martinez", "email": "miguelitomiguelon@grefusa.com", "password": "pollagorda69"}'
    
    test many:
    curl -X POST "http://127.0.0.1:8000/api/users/" -H "Content-Type: application/json" -d '[{"name": "Miguel Gutierrez Martinez", "email": "miguelitomiguelon@grefusa.com", "password": "pollagorda69"}, {"name": Tupac Shakur, "email": "westcoast@usa.gov", "password": "wHoKilled2PaK?"}'
    """
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('users')
        if code == 1: # Hay que cambiar los codigos de error
            # raise DbConnException(msg, code)
            raise ValueError(msg)

        # Este control de errores se deberia hace en la clase DbConn
        if conn.exists({'email': user.email}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email {user.email} ya registrado")

        hash_pwd = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

        new_user = {
            'name': user.name,
            'email': user.email,
            'password': hash_pwd.decode("utf-8")
        }

        code, result = conn.insert(data_dict=new_user)
        if code == 1:
            raise ValueError(result)

        return JSONResponse(content=result)
    except HTTPException as e:
        # ErrorHandler.handle_fastapi_error(e)
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(error=e))
    except PyMongoError as e:
        # ErrorHandler.handle_pymongo_error(e)
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(error=e))
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        # print(f"\n---create_user() error---\n{e}")
        return JSONResponse(content=ErrorHandler.handle_general_error(error=e))
# consultar un usuario por email

# cambiar esto para que el email no sea parte del endpoint sino se interprete como query
# asi FastAPI no se confunde con el id


@router.get(
    '/users/email/{email:str}',
    response_description="get user by email",
    status_code=status.HTTP_200_OK)
async def get_user(email: EmailStr) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('users')
        
        if code == 1:
            raise ValueError(msg)
        
        # Este control de errores se deberia hace en la clase DbConn
        if not conn.exists({'email': email}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"usuario {email} no encontrado")

        code, res = conn.query({'email': email})

        if code == 1:
            raise ValueError(res)
        
        return JSONResponse(content=res)

    except PyMongoError as e:
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(error=e))
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        # print(f"\n---get_user() error---\n{e}")
        return JSONResponse(content=ErrorHandler.handle_general_error(error=e))


@router.get(
    "/users/id/{user_id:str}",
    response_description="get user by _id",
    status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id:str):
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('users')
        if not conn.exists({"_id":ObjectId(user_id)}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"usuario {user_id} no encontrado")
        code,msg = conn.query({"_id":ObjectId(user_id)})
        print(msg)
        return JSONResponse(content=msg)
    except PyMongoError as e:
        pass
    except HTTPException as e:
        pass
    except Exception as e:
        pass

@router.put(
    '/users/',
    response_description="update user by email",
    status_code=status.HTTP_200_OK)
async def modify_user(user: PostUser) -> JSONResponse:
    """
    test:
    (sin pwd) curl -X PUT http://192.168.160.80:8000/api/users/ -H "Content-Type: application/json" -d '{"name": "2Pac", "email": "miguelitomiguelon@grefusa.com"}'
    (sin nombre) curl -X PUT http://192.168.160.80:8000/api/users/ -H "Content-Type: application/json" -d '{"email": "miguelitomiguelon@grefusa.com", "password": "skere69"}'
    """
    try:
        conn = DbConn('sample_mflix')
        code, msg = conn.connect('users')

        if code == 1:
            # raise DbConnException(message=msg, error_code=code)
            raise ValueError(msg)

        # Este control de errores se deberia hace en la clase DbConn
        if not conn.exists({'email': user.email}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El usuario {user.email} no se encuentra en la base de datos")

        # solo se contempla la modificacion de un documento de la coleccion. 
        # La idea es que se puedan modificar mas de uno a la vez
        mod_dict = {}
        if user.name != None:
            mod_dict['name'] = user.name
        if user.password != None:
            hash_pwd = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
            mod_dict['password'] = hash_pwd.decode('utf-8')

        code, msg = conn.update(query_dict={'email': user.email}, modify_dict=mod_dict)

        if code == 1:
            # raise DbConnException(msg, code)
            raise ValueError(msg)

        return JSONResponse(content=msg)
    except PyMongoError as e:
        # ErrorHandler.handle_dbconn_error(e)
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(error=e))
    except HTTPException as e:
        # ErrorHandler.handle_fastapi_error(e)
        return JSONResponse(content=ErrorHandler.handle_fastapi_error(error=e))
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        # print(f"---modify_user() error---\n{e}")
        return JSONResponse(content=ErrorHandler.handle_general_error(error=e))

# verificar
@router.delete(
    '/users/{email}',
    response_description="Delete user by email",
    status_code=status.HTTP_200_OK)
async def delete_user(email: EmailStr) -> JSONResponse:
    try:
        conn = DbConn('sample_mflix')
        if conn is None:
            raise ValueError("conn is none")
        
        code, msg = conn.connect('users')

        if code == 1:
            # raise DbConnException(msg, code)
            raise ValueError(msg)

        code, msg = conn.delete(query_dict={'email': email})

        if code == 0:
            # raise DbConnException(msg, code)
            raise ValueError(msg)
        
        return JSONResponse(content=msg)

    except PyMongoError as e:
        # errorMsg = ErrorHandler.handle_pymongo_error(e)
        # print(errorMsg)
        return JSONResponse(content=ErrorHandler.handle_pymongo_error(error=e))
    except Exception as e:
        # errorMsg = ErrorHandler.handle_general_error(e)
        # print(errorMsg)
        return JSONResponse(content=ErrorHandler.handle_general_error(error=e))
    
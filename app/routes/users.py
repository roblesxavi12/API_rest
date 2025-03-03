from fastapi import APIRouter, HTTPException, status
from pymongo.errors import PyMongoError
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
async def serve_data():
    try:
        conn = DbConn('sample_mflix', 'users')

        code, msg = conn.connect()
        if code == 1:
            raise DbConnException(message=msg, error_code=code)

        # code, msg = conn.query({"name": {"$regex": "^N"}}) # devuelve todas las entradas que el nombre empiece por N
        code, msg = conn.query({})
        if code == 1:
            raise DbConnException(message=msg, error_code=code)
        
        return JSONResponse(content=msg)

    except DbConnException as e:
        # ErrorHandler.handle_dbconn_error(e)
        pass
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        print(f"\n---serve_data() error---\n{e}\ntipo del error: {type(e).__name__}")
        return JSONResponse(content={'error':str(e)})

# crear un nuevo usuario
@router.post(
    "/users/",
    response_description="add new user",
    response_model=dict,
    status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """
    test one:
    curl -X POST "http://127.0.0.1:8000/api/users/" -H "Content-Type: application/json" -d '{"name": "Miguel Gutierrez Martinez", "email": "miguelitomiguelon@grefusa.com", "password": "pollagorda69"}'
    
    test many:
    curl -X POST "http://127.0.0.1:8000/api/users/" -H "Content-Type: application/json" -d '[{"name": "Miguel Gutierrez Martinez", "email": "miguelitomiguelon@grefusa.com", "password": "pollagorda69"}, {"name": Tupac Shakur, "email": "westcoast@usa.gov", "password": "wHoKilled2PaK?"}'
    """
    try:
        conn = DbConn('sample_mflix', 'users')
        code, msg = conn.connect()
        if code == 1: # Hay que cambiar los codigos de error
            raise DbConnException(msg, code)

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

        return result
    except HTTPException as e:
        # ErrorHandler.handle_fastapi_error(e)
        pass
    except DbConnException as e:
        # ErrorHandler.handle_dbconn_error(e)
        pass
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        print(f"\n---create_user() error---\n{e}")
        return JSONResponse(content={'error': str(e)})

# consultar un usuario por email
@router.get(
    '/users/{email}',
    response_description="get user by email",
    status_code=status.HTTP_200_OK)
async def get_user(email: EmailStr):
    try:
        conn = DbConn('sample_mflix', 'users')
        code, msg = conn.connect()
        
        if code == 1:
            raise ValueError(msg)
        
        # Este control de errores se deberia hace en la clase DbConn
        if not conn.exists({'email': email}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"usuario {email} no encontrado")

        code, res = conn.query({'email': email})

        if code == 1:
            raise ValueError(res)
        
        return JSONResponse(content=res)
    except DbConnException as e:
        # ErrorHandler.handle_dbconn_error(e)
        pass
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        print(f"\n---get_user() error---\n{e}")
        return JSONResponse(content={'error': str(e)})

@router.put(
    '/users/',
    response_description="update user by email",
    status_code=status.HTTP_200_OK)
async def modify_user(user: PostUser):
    """
    test:
    (sin pwd) curl -X PUT http://192.168.160.80:8000/api/users/ -H "Content-Type: application/json" -d '{"name": "2Pac", "email": "miguelitomiguelon@grefusa.com"}'
    (sin nombre) curl -X PUT http://192.168.160.80:8000/api/users/ -H "Content-Type: application/json" -d '{"email": "miguelitomiguelon@grefusa.com", "password": "skere69"}'
    """
    try:
        conn = DbConn('sample_mflix', 'users')
        code, msg = conn.connect()

        if code == 1:
            raise DbConnException(message=msg, error_code=code)

        # Este control de errores se deberia hace en la clase DbConn
        if not conn.exists({'email': user.email}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El usuario {user.email} no se encuentra en la base de datos")

        # este bloque de codigo no deberia hacer falta
        # code, msg = conn.query({'email': user.email})
        # if code == 1:
            # raise DbConnException(msg, code)

        # Contempla que solo se devuelve 1 documento ( 1 usuario )
        # En realidad se deberia buscar para obtener la clave e insertar al usuario que toca

        mod_dict = {}
        if user.name != None:
            mod_dict['name'] = user.name
        if user.password != None:
            hash_pwd = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
            mod_dict['password'] = hash_pwd.decode('utf-8')

        code, msg = conn.update(query_dict={'email': user.email}, modify_dict=mod_dict)

        if code == 1:
            raise DbConnException(msg, code)

        return JSONResponse(content=msg)
    except DbConnException as e:
        # ErrorHandler.handle_dbconn_error(e)
        pass
    except HTTPException as e:
        # ErrorHandler.handle_fastapi_error(e)
        pass
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        print(f"---modify_user() error---\n{e}")
        return JSONResponse(content={'error': str(e)})

# verificar
@router.delete(
    '/users/{email}',
    response_description="Delete user by email",
    status_code=status.HTTP_200_OK)
async def delete_user(email: EmailStr):
    try:
        conn = DbConn('sample_mflix', 'users')
        if conn is None:
            raise ValueError("conn is none")
        
        code, msg = conn.connect()

        if code == 1:
            raise DbConnException(msg, code)

        code, msg = conn.delete(query_dict={'email': email})

        if code == 1:
            raise DbConnException(msg, code)
        
        return msg

    except DbConnException as e:
        # ErrorHandler.handle_dbconn_error(e)
        pass
    except Exception as e:
        # ErrorHandler.handle_general_error(e)
        print(f"---delete_user() error---\n{e}")
        return JSONResponse(content={'error': str(e)})
    
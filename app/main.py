# dummy code para entender minimamente como funciona pymongo
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from app.routes import users, theaters, movies

# https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform -> create authentication
# run fastapi server -> python app/main.py desde la carpeta mongo_test
# http://192.168.160.80:8000/users

# entrar en el venv -> venv\Scripts\activate
# salir del venv -> deactivate
# ejecutar con python -m app.main (desde dentro del venv)
app = FastAPI(title="Test app")
app.include_router(users.router, prefix='/api', tags=['users'])
app.include_router(theaters.router, prefix='/api', tags=['theaters'])
app.include_router(movies.router, prefix='/api', tags=['movies'])

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn.run("app.main:app", host="192.168.1.39", port=8000, reload=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
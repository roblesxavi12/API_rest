# from pymongo.mongo_client import MongoClient,
from bson.objectid import ObjectId
from pymongo.errors import *
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo import ReturnDocument, MongoClient, AsyncMongoClient
from pymongo.errors import PyMongoError, OperationFailure
from pymongo.server_api import ServerApi
import json
from typing import Tuple, Union, Union
import os
from dotenv import load_dotenv
from app.errorHandler import ErrorHandler
from app.exceptions import DbConnException
from retrying import retry
from time import perf_counter

# https://pymongo.readthedocs.io/en/stable/api/pymongo/errors.html
# https://pymongo.readthedocs.io/en/stable/tutorial.html#getting-a-single-document-with-find-one


# ADAPTAR LA CLASE A UN PATRON SINGLETON
# https://refactoring.guru/es/design-patterns/singleton
# https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/

# ADAPTAR LA CLASE AL USO DE ASYNC/AWAIT


class DbConn:
    _instance = None
    _created = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DbConn, cls).__new__(cls)
            print("\nCreando instancia nueva\n")
        return cls._instance

    def __init__(self, dbname: str):
        
        if self._created == False:
            print(f"Inicializando instancia nueva")
            load_dotenv()
            self.dbname = dbname # De momento deberia ser siempre 'sample_mflix'
            # self.colname = colname # Aqui si que tenemos distintas colecciones
            self.db = None
            self.collection = None
            self.client = None
            self.user = os.getenv("MONGO_USER")
            self.pwd = os.getenv("MONGO_PASSWORD")
            self.uri = f"mongodb+srv://{self.user}:{self.pwd}@testcluster.3kxrn.mongodb.net/?retryWrites=true&w=majority&appName=testCluster"
            self._created = True

    def connect(self, colname: str) -> Union[Tuple[int, dict[str, str]], Tuple[int, str]]:
        """
        No hay posibles errores propios de la funcion, solo errores de las funciones de pymongo -> No hace falta return
        """
        t1 = perf_counter()
        try:
            # raise OperationFailure("test")
            self.client = AsyncMongoClient(self.uri, server_api=ServerApi('1'))
            self.db = self.client[self.dbname]
            self.collection = self.db[colname]

            t2 = perf_counter()
            total = t2 - t1
            return 0, {"OK": "Conexion realizada con exito"}
        except PyMongoError as e:
            errorMsg = ErrorHandler.handle_pymongo_error(e)
            # errorMsg = f"---dbConn class error---\n---connect() function---\nError: {e}"
            print("---connect()---\nPyMongoErrorCase",errorMsg)
            t2 = perf_counter()
            total = t2 - t1
            return 1, errorMsg
        except Exception as e:
            errorMsg = ErrorHandler.handle_general_error(e)
            # errorMsg = f"---dbConn class error---\n---connect() function---\nError: {e}"
            print("---connect---\nGeneral error case",errorMsg)
            t2 = perf_counter()
            total = t2 - t1
            return 1, errorMsg # El return se tiene que eliminar
    
    # Se deberia probar con wait_exponential_multiplier y wait_exponential_max
    # retry_on_exception=lambda err: isinstance(err, AutoReconnect) -> no se hace asi para abstraer la clase ErrorHandler lo maximo posible
    @retry(retry_on_exception=ErrorHandler.pymongo_autoreconnect_error, stop_max_attempt_number=5, wait_fixed=2000) # 2s wait
    async def query(self, query_dict: dict, limit: int) -> Union[Tuple[int, str], Tuple[int, list], Tuple[int, dict[str,str]]]:
        # Adaptar para el uso de find_one y find_many. mirar la funcion insert() como ejemplo
        """
        si excedes el limite de documentos devuelve el maximo
        """
        try:
            # falta hacer control de erroes
            # raise ExecutionTimeout("test error")
            data_list = []
            # Si no se puede establecer conexion y se llega a esta funcion no se lanzaba un pymongoerror,
            # Sino un atributeError porque self.collection es None
            if self.collection == None:
                raise ConnectionFailure("Could not retrieve a collection") #solucion chapucera

            if limit > 0:
                data = self.collection.find(query_dict).limit(limit)
                if not data:
                    raise OperationFailure("cursor data is none")
                aux_dict = {}
                cnt = await self.collection.count_documents(query_dict)
                if cnt >= 1:
                    for x in data:
                        # data_list.append({x1:y1 for (x1, y1) in zip(x.keys(),x.values()) if x1 != '_id'})
                        # data_list.append({x1:y1 for (x1,y1) in zip(x.keys(),x.values())})
                        data_list.append({x1:str(y1) if x1 == '_id' else y1 for (x1,y1) in zip(x.keys(), x.values())})
            # print(data_list)
                return 0, jsonable_encoder(data_list)
            else:
                data = self.collection.find(query_dict)
                aux_dict = {}
                cnt = await self.collection.count_documents(query_dict)
                if cnt >= 1:
                    for x in data:
                        # data_list.append({x1:y1 for (x1, y1) in zip(x.keys(),x.values()) if x1 != '_id'})
                        # data_list.append({x1:y1 for (x1,y1) in zip(x.keys(),x.values())})
                        data_list.append({x1:str(y1) if x1 == '_id' else y1 for (x1,y1) in zip(x.keys(), x.values())})
            # print(data_list)
                return 0, jsonable_encoder(data_list)
        except PyMongoError as e:
            errorMsg = ErrorHandler.handle_pymongo_error(e)
            # errorMsg = f"---dbConn class error---\n---query() function---\nError: {e}"
            print("---query()---\nPyMongoError", errorMsg)
            return 1, errorMsg
        except Exception as e:
            # errorMsg = f"---dbConn class error---\n---query() function---\nError: {e}"
            errorMsg = ErrorHandler.handle_general_error(e)
            print("---query()---\nGeneralError", errorMsg)
            return 1, errorMsg

    @retry(retry_on_exception=ErrorHandler.pymongo_autoreconnect_error, stop_max_attempt_numer=5, wait_fixed=2000) # 2s wait
    async def insert(self, data_dict: Union[dict, list]) -> Union[Tuple[int, list[dict[str, str]]], Tuple[int, str], Tuple[int, dict[str,str]]]:
        """
        if data_dict is a dict -> pymongo.insert_one()
        if data_dict is a list -> pymongo.insert_many()
        """
        try:
            # if not isinstance(data_dict, dict) or not isinstance(data_dict, list):
            #     raise TypeError("el parametro no es un diccionario. TERMINAR MENSAJE DE ERROR")
            
            if type(data_dict).__name__ not in (type([]).__name__, type({}).__name__):
                raise TypeError(f"Se esperaba un dict o un list pero se ha recibido un {type(data_dict).__name__}")
            
            if not data_dict:
                raise ValueError("Empty dictionary")

            if self.collection is None:
                raise ValueError("self.collection no deberia ser None")

            if isinstance(data_dict, dict) or len(data_dict) == 1:
                # caso insertar 1 elemento -> pymongo.insert_one()
                res = await self.collection.insert_one(data_dict)
                # comprobar valor de retorno y handlear la exception como es debido
                if res == None:
                    raise ValueError("res is None") # cambiar

                return 0, {"id": str(res.inserted_id)}
            elif isinstance(data_dict, list) and len(data_dict) > 1:
                # caso insertar varios elementos, bulk insert -> pymongo.insert_many()
                res = self.collection.insert_many(data_dict)

                # comprobar valor de retorno y handlear la exception como es debido
                if res == None:
                    raise ValueError("res is None") # Cambiar

                return 0, [{"id":x} for x in res.inserted_ids]
            else:
                raise ValueError("Should not arrived here") # better handling
        except PyMongoError as e:
            return 1, ErrorHandler.handle_pymongo_error(e)
        except Exception as e:
            return 1, ErrorHandler.handle_general_error(e)

    @retry(retry_on_exception=ErrorHandler.pymongo_autoreconnect_error, stop_max_attempt_number=5, wait_fixed=2000) # 2s wait
    def exists(self, query_dict: Union[dict[str, str], dict[str, int], dict[str, dict[str, list]], dict[str, ObjectId]]) -> Union[bool,None, Tuple[int, dict[str,str]]]:
        try:
            if self.collection == None:
                raise ValueError("self.collecion is None")
            elif self.collection.find_one(query_dict): # Hay que cambiar esto por self.query(query_dict,1)
                return True
            return False

        except PyMongoError as e:
            return 1, ErrorHandler.handle_pymongo_error(e)
        except Exception as e:
            return 1, ErrorHandler.handle_general_error(e)

    @retry(retry_on_exception=ErrorHandler.pymongo_autoreconnect_error, stop_max_attempt_number=5, wait_fixed=2000) # 2s wait
    def delete(self, query_dict: dict) -> Union[Tuple[int, dict[str, str]], Tuple[int, str]] :
        """
        MIRAR COMO FUNCIONA delete_one()
        ADAPTAR PARA EL USO DE delete_many()
        """
        try:
            if self.collection == None:
                raise ValueError("self.collection is None")

            res = self.collection.delete_one(query_dict)
            if res == None:
                raise ValueError("res is None")

            if res.deleted_count == 0:
                raise OperationFailure(str(res.raw_result))

            return 0, {"deleted":f"{res.acknowledged}"}

        except PyMongoError as e:
            # ErrorHandler.handle_pymongo_error(e)
            msg = f"---dbConn class error---\n---delete() function---\nError: {e}"
            return 1, msg
        except Exception as e:
            # ErrorHandler.handle_general_error()
            msg = f"---dbConn class error---\n---delete() function---\nError: {e}"
            return 1, msg
    
    @retry(retry_on_exception=ErrorHandler.pymongo_autoreconnect_error, stop_max_attempt_number=5, wait_fixed=2000) # 2s wait
    def update(self, query_dict: dict, modify_dict: dict) -> Union[Tuple[int, str], Tuple[int,list], Tuple[int, dict[str,str]]]:
        """
        query_dict -> diccionario con la consulta, modify_dict -> diccionario con parametros a cambiar
        """
        try:
            if not isinstance(modify_dict, dict):
                raise TypeError(f"dict for modify_dict parameter expected. {type(modify_dict).__name__} obtained\n")
            elif not isinstance(query_dict, dict):
                raise TypeError(f"dict for query_dict parameter expected. {type(query_dict).__name__} obtained\n")
           
            if query_dict == {} or modify_dict == {}:
                raise ValueError(f"Empty dictionary not supported\n")
            if self.collection == None:
                raise ValueError("self.collection is None")
            
            # falta adaptarlo para bulk update, muy hardcoded
            # No hay una operacion que haga bulk update por defecto
            """
            # diccionario de diccionarios?
            # ahora mismo implementado pensando que ambos parametros son listas de diccionarios
            for (x,y) in zip(query_dict, modify_dict):
                msg = self.collection.find_one_and_update(x, {'$set':y}, return_document=ReturnDocument.AFTER)
                if msg == None:
                    raise OperationFailure(f"query {x} not found\n")
            """
            msg = self.collection.find_one_and_update(query_dict, {'$set': modify_dict}, return_document=ReturnDocument.AFTER)

            if msg == None:
                raise OperationFailure(f"query {query_dict} not found\n") # PyMongoError
            
            data_l = []
            # se elimina el '_id' de cada documento y se convierte la query en una lista
            # sirve tanto como para 1 o varios. Si es solo 1 hara 1 iter.
            for x in msg:
                data_l.append({x1:y1 for (x1,y1) in zip(msg.keys(),msg.values()) if x1 != '_id'})

            return 0, data_l
        except PyMongoError as e:
            # msg = f"---DbConn class error---\n---update() function---\n{e}"
            return 1, ErrorHandler.handle_pymongo_error(error=e)
        except Exception as e:
            # msg = f"---DbConn class error---\n---update() function---\n{e}"
            return 1, ErrorHandler.handle_general_error(error=e)

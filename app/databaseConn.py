# from pymongo.mongo_client import MongoClient
# from pymongo.errors import *
from pymongo import ReturnDocument, MongoClient, errors
from pymongo.errors import PyMongoError, OperationFailure
from pymongo.server_api import ServerApi
import json
from typing import Tuple, Union, Union
import os
from dotenv import load_dotenv
from app.errorHandler import ErrorHandler
from app.exceptions import DbConnException

# https://pymongo.readthedocs.io/en/stable/api/pymongo/errors.html
# https://pymongo.readthedocs.io/en/stable/tutorial.html#getting-a-single-document-with-find-one


# ADAPTAR LA CLASE A UN PATRON SINGLETON
# https://refactoring.guru/es/design-patterns/singleton
# https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/


class DbConn:
    _instance = None
    _created = False

    """
    old __init__

    def __init__(self, dbname: str, colname: str): # uri: str
        if not isinstance(dbname, str):
            raise TypeError(f"La variable dbname debe ser del tipo string pero se recibio {type(dbname).__name__}")
        elif not isinstance(colname, str):
            raise TypeError(f"La variable colname debe ser del tipo string pero se recibio {type(colname).__name__}")
        
        load_dotenv()
        self.dbname = dbname # De momento deberia ser siempre 'sample_mflix'
        self.colname = colname # Aqui si que tenemos distintas colecciones
        self.db = None
        self.collection = None
        self.client = None
        self.user = os.getenv("MONGO_USER")
        self.pwd = os.getenv("MONGO_PASSWORD")
        # seria ideal crear un inicio de sesion para la bd, una coleccion especifica para eso. Diferente de users
        # self.uri = "mongodb+srv://roblesxavi12:H0Nk1rNxpE5FK3NR@testcluster.3kxrn.mongodb.net/?retryWrites=true&w=majority&appName=testCluster"
        self.uri = f"mongodb+srv://{self.user}:{self.pwd}@testcluster.3kxrn.mongodb.net/?retryWrites=true&w=majority&appName=testCluster"
    """

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DbConn, cls).__new__(cls)
            print("\nCreando instancia nueva\n")
        return cls._instance

    def __init__(self, dbname: str, colname: str):
        # falta un bloque try-except?
        if not isinstance(dbname, str):
            raise TypeError(f"La variable dbname debe ser del tipo string pero se recibio {type(dbname).__name__}")
        elif not isinstance(colname, str):
            raise TypeError(f"La variable colname debe ser del tipo string pero se recibio {type(colname).__name__}")
        
        if self._created == False:
            print(f"\nInicializando instancia nueva\nCreated: {self._created}\n")
            load_dotenv()
            self.dbname = dbname # De momento deberia ser siempre 'sample_mflix'
            self.colname = colname # Aqui si que tenemos distintas colecciones
            self.db = None
            self.collection = None
            self.client = None
            self.user = os.getenv("MONGO_USER")
            self.pwd = os.getenv("MONGO_PASSWORD")
            self.uri = f"mongodb+srv://{self.user}:{self.pwd}@testcluster.3kxrn.mongodb.net/?retryWrites=true&w=majority&appName=testCluster"
            self._created = True

    def connect(self) -> Union[Tuple[int, dict[str, str]], Tuple[int, str]]:
        """
        No hay posibles errores propios de la funcion, solo errores de las funciones de pymongo -> No hace falta return
        """
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.db = self.client[self.dbname]
            self.collection = self.db[self.colname]

            return 0, {"OK": "Conexion realizada con exito"}
        except PyMongoError as e:
            # ErrorHandler.handle_pymongo_error(e)
            errorMsg = f"---dbConn class error---\n---connect() function---\nError: {e}"
            return 1, errorMsg
        except Exception as e:
            # ErrorHandler.handle_general_error(e)
            errorMsg = f"---dbConn class error---\n---connect() function---\nError: {e}"
            return 1, errorMsg # El return se tiene que eliminar

    def query(self, query_dict: dict) -> Union[Tuple[int, str], Tuple[int, list]]:
        # Adaptar para el uso de find_one y find_many. mirar la funcion insert() como ejemplo
        """
        hay que mejorar esto, es muy primigenio
        if query_dict is a empty dict -> pymongo.find_one()
        if not -> pymongo.find()
        """
        try:
            # print(query_dict, type(query_dict).__name__)
            if not isinstance(query_dict, dict):
                raise TypeError(f"Se esperaba una variable del tipo {type({'1':1}).__name__} pero se ha obtenido una del tipo {type(query_dict).__name__}.")
            
            # falta hacer control de erroes
            data_list = []
            if self.collection == None:
                raise ValueError("self.collection es None")

            if query_dict == {}:
                # caso find (mas de un documento)
                data = self.collection.find(query_dict)
                for x in data:
                    data_list.append({x1:y1 for (x1, y1) in zip(x.keys(),x.values()) if x1 != '_id'})
            else:
                # caso find one (un solo documento)
                data = self.collection.find_one(query_dict)
                if data == None:
                    raise ValueError("data is None")

                data_list.append({x1:y1 for (x1,y1) in zip(data.keys(), data.values()) if x1 != '_id'})
            
            return 0, data_list
        except errors.PyMongoError as e:
            # Error.handle_pymongo_error(e)
            errorMsg = f"---dbConn class error---\n---query() function---\nError: {e}"
            return 1, errorMsg
        except Exception as e:
            errorMsg = f"---dbConn class error---\n---query() function---\nError: {e}"
            # ErrorHandler.handle_general_error(e)
            return 1, errorMsg

    def insert(self, data_dict: Union[dict, list]) -> Union[Tuple[int, list[dict[str, str]]], Tuple[int, str], Tuple[int, dict[str,str]]]:
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
            if isinstance(data_dict, dict):
                # caso insertar 1 elemento -> pymongo.insert_one()
                res = self.collection.insert_one(data_dict)
                if res == None:
                    raise ValueError("res is none")
                # control de errores
                return 0, {"id": str(res.inserted_id)}
            elif isinstance(data_dict, list):
                # caso insertar varios elementos, bulk insert -> pymongo.insert_many()
                res = self.collection.insert_many(data_dict)
                if res == None:
                    raise ValueError("res is None")
                # control de erroes

                # Comprobar si el valor de retorno es adecuado para hacer esto 
                return 0, [{"id":x} for x in res.inserted_ids]
        except errors.PyMongoError as e:
            # ErrorHandler.handle_pymongo_error(e)
            return 1, f"---insert() error---\n{e}\n"
            pass
        except Exception as e:
            # ErrorHandler.handle_general_error(e)
            return 1, f"---insert() error---\n{e}\n"

    def exists(self, query_dict) -> Union[bool,None]:
        try:
            if self.collection == None:
                raise ValueError("self.collecion is None")
            if not isinstance(query_dict, dict):
                raise TypeError("se esperaba un dict") 
            elif self.collection.find_one(query_dict):
                print("Encontrado")
                return True
            return False

        except errors.PyMongoError as e:
            # ErrorHandler.handle_pymongo_error(e)
            pass
        except Exception as e:
            # ErrorHandler.handle_general_error(e)
            print(e)

    def delete(self, query_dict: dict) -> Union[Tuple[int, bool], Tuple[int, str]] :
        """
        MIRAR COMO FUNCIONA delete_one()
        ADAPTAR PARA EL USO DE delete_many()
        """
        try:
            if not isinstance(query_dict, dict):
                raise TypeError(f"Se esperaba una variable del tipo {type({'1':1}).__name__} pero se ha obtenido una del tipo {type(query_dict).__name__}.")
            
            if self.collection == None:
                raise ValueError("self.collection is None")

            res = self.collection.delete_one(query_dict)
            if res == None:
                raise ValueError("res is None")

            if res.deleted_count == 0:
                raise errors.OperationFailure(str(res.raw_result))

            return 0, res.acknowledged

        except errors.PyMongoError as e:
            # ErrorHandler.handle_pymongo_error(e)
            msg = f"---dbConn class error---\n---delete() function---\nError: {e}"
            return 1, msg
        except Exception as e:
            # ErrorHandler.handle_general_error()
            msg = f"---dbConn class error---\n---delete() function---\nError: {e}"
            return 1, msg
    
    def update(self, query_dict: dict, modify_dict: dict) -> Union[Tuple[int, str], Tuple[int,list]]:
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
            
            msg = self.collection.find_one_and_update(query_dict, {'$set': modify_dict}, return_document=ReturnDocument.AFTER)

            if msg == None:
                raise OperationFailure(f"query {query_dict} not found\n") # PyMongoError
            
            # se elimina el '_id' de cada documento y se convierte la query en una lista
            data_l = []
            # hardcoded af
            data_l.append({x1:y1 for (x1,y1) in zip(msg.keys(),msg.values()) if x1 != '_id'})

            return 0, data_l
        except PyMongoError as e:
            # ErrorHandler.handle_pymongo_error()
            msg = f"---DbConn class error---\n---update() function---\n{e}"
            return 1, msg
        except Exception as e:
            msg = f"---DbConn class error---\n---update() function---\n{e}"
            return 1, msg

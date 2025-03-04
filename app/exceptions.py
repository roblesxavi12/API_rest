from typing import Union
from pymongo.errors import PyMongoError
# dummy class af
class DbConnException(PyMongoError):
    def __init__(self, message: Union[dict[str, str], list, str], error_code: int):
        self.msg = message
        self.error_code = error_code
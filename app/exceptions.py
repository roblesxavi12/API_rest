
class DbConnException(Exception):
    def __init__(self, message, error_code):
        if not isinstance(message, str):
            raise TypeError("el mensaje debe ser un string")
        if not isinstance(error_code, int):
            raise TypeError("El codigo de error debe ser un int")
        
        self.msg = message
        self.error_code = error_code
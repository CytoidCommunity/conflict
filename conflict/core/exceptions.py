from typing import Optional


class ApiFailed(Exception):
    def __init__(self, code: Optional[int] = None, message: Optional[str] = None, *args, **kwargs):
        self.code = code
        self.message = message

    def __repr__(self):
        return f"<{self.__class__.__name__}, code={self.code}, msg={self.message}>"

    def __str__(self):
        return self.__repr__()

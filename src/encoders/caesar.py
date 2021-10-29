from typing import IO, Callable, AnyStr
import tempfile

from src.consts import ENGLISH_ALPHABET, RUSSIAN_ALPHABET, ENCODING
from src.encoders.shennon import ShennonEncoder, ShennonDecoder


class CaesarEncoder(ShennonEncoder):
    def __init__(self, data: str, writer: IO, progress_callback: Callable[[int, int], None], key: int = 0):
        super().__init__(data, writer, progress_callback)
        self.key = key

    def write_symbol(self, symbol):
        symbol = symbol + self.key
        if symbol > 255:
            symbol -= 255

        super(CaesarEncoder, self).write_symbol(symbol)

    def write(self):
        super(CaesarEncoder, self).write()


class CaesarDecoder(ShennonDecoder):
    def __init__(self, reader: IO, writer: IO, progress_callback: Callable[[int, int], None], key: int = 0):
        super().__init__(reader, writer, progress_callback)
        self.key = key
        
    def get_char(self, n: int):
        n = n - self.key
        if n < 0:
            n += 255

        return super(CaesarDecoder, self).get_char(n)

    def read(self):
        super(CaesarDecoder, self).read()


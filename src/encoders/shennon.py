from collections import Counter
from math import ceil, log2
from typing import IO, Callable

from src.consts import ENCODING, SYMBOL_SEPARATOR, SYMBOL_LENGTH, INT_LENGTH, MAGIC_SEPARATOR, MAGIC_HEADER, BYTE_ORDER
from src.encoders.base import Encoder, Decoder
from src.utils import get_binary


def create_bx(probabilities):
    bx = [(probabilities[0][0], 0.0)]

    for i, item in enumerate(probabilities):
        res = sum([item[1] for item in probabilities[:i]])
        bx.append((item[0], res))

    del bx[1]

    return bx


def generate_codes(probabilities, bx):
    binarized = [(item[0], get_binary(item[1])) for item in bx]
    binarized[0] = (binarized[0][0], '0.0000000000000000000000000000000000000')
    res = [(item[0], item[1][2:ceil(abs(log2(probabilities[i][1]))) + 2]) for i, item in
           enumerate(binarized)]

    codes = dict({item[0]: item[1] for item in res})

    return codes


class ShennonEncoder(Encoder):
    def __init__(self, data: str, writer: IO, progress_callback: Callable[[int, int], None]):
        super().__init__(data, writer, progress_callback)

    def get_symbols(self):
        counter = Counter(self.data)
        return [(ord(key), value) for key, value in counter.most_common()]

    def get_probabilities(self, symbols):
        return [(item[0], item[1] / self.data_length) for item in symbols]

    def encrypt_data(self, codes):
        s = ''
        for item in self.data:
            s += codes[ord(item)]

        return s

    def initialize_archive(self):
        self.writer.write(MAGIC_HEADER)

    def next_section(self):
        self.writer.write(MAGIC_SEPARATOR)

    def write_int(self, n: int, length: int):
        self.writer.write(n.to_bytes(length, BYTE_ORDER))

    def write_symbol(self, symbol):
        self.write_int(symbol, SYMBOL_LENGTH)

    def write(self):
        symbols = self.get_symbols()
        probabilities = self.get_probabilities(symbols)

        bx = create_bx(probabilities)
        codes = generate_codes(probabilities, bx)

        data = self.encrypt_data(codes)

        # write data to archive
        self.initialize_archive()

        data_length = len(data)
        self.write_int(data_length, INT_LENGTH)

        # write alphabet
        for item in codes.keys():
            self.write_symbol(item)

        self.next_section()

        # write symbols' codes
        for item in codes.values():
            self.writer.write(item.encode(ENCODING))
            self.writer.write(SYMBOL_SEPARATOR)

        self.next_section()

        # write data
        if len(data) % 8 != 0:
            data += '0' * (len(data) % 8)

        for i in range(0, len(data), 8):
            s = data[i:i + 8]
            n = int(s, 2)
            self.write_int(n, 1)

            if self.progress_callback is not None:
                self.progress_callback(data_length, i)


class ShennonDecoder(Decoder):
    def __init__(self, reader: IO, writer: IO, progress_callback: Callable[[int, int], None]):
        super().__init__(reader, writer, progress_callback)

    def read_int(self, length: int) -> int:
        n = self.reader.read(length)
        return int.from_bytes(n, BYTE_ORDER)

    def get_char(self, n: int):
        return chr(n)

    def read(self):
        header = self.reader.read(len(MAGIC_HEADER))
        if header != MAGIC_HEADER:
            raise TabError()

        data_length = self.read_int(INT_LENGTH)
        alphabet = dict()

        # read alphabet
        symbols_part = bytes()
        while not symbols_part.endswith(MAGIC_SEPARATOR):
            symbols_part += self.reader.read(SYMBOL_LENGTH)
        symbols_part = symbols_part.replace(MAGIC_SEPARATOR, bytes())

        for i in range(0, len(symbols_part), SYMBOL_LENGTH):
            n = int.from_bytes(symbols_part[i:i + SYMBOL_LENGTH], BYTE_ORDER)
            n = self.get_char(n)
            alphabet[n] = ''

        # read codes
        keys = list(alphabet.keys())
        code = bytes()
        i = 0
        while code != MAGIC_SEPARATOR:
            code += self.reader.read(1)

            if code.endswith(SYMBOL_SEPARATOR):
                code = code.replace(SYMBOL_SEPARATOR, bytes())
                key = keys[i]
                alphabet[key] = code.decode(ENCODING)

                code = bytes()
                i += 1

        codes = {v: k for k, v in alphabet.items()}

        # read data
        data_encoded = ''
        while len(data_encoded) < data_length:
            n = self.read_int(1)
            data_encoded += bin(n)[2:].rjust(8, '0')

        data_encoded = data_encoded[:data_length]

        # decode data
        current = ''
        i = 0
        while i < data_length:
            current += data_encoded[i]
            i += 1

            if current in codes:
                self.writer.write(codes[current])
                current = ''

                if self.progress_callback is not None:
                    self.progress_callback(data_length, i)

# STRUCTURE:
# MAGIC_HEADER
# DATA_LENGTH
# LETTER[]
# MAGIC_SEPARATOR
# CODE[]
# MAGIC_SEPARATOR
# DATA

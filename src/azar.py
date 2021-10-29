import os.path
from enum import Enum
from typing import Type, Union, Callable

from src.consts import ENCODING
from src.encoders.base import Encoder, Decoder

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class AzarArchiveMode(Enum):
    Read = 1
    Write = 2


class AzarArchive:
    def __init__(self, path: str, out_path: str, mode_processor: Type[Union[Encoder, Decoder]],
                 progress_callback: Callable[[int, int], None] = None, finish_callback: Callable[[], None] = None):
        assert os.path.exists(path)

        self.finish_callback = finish_callback

        self.mode = AzarArchiveMode.Write if issubclass(mode_processor, Encoder) else AzarArchiveMode.Read

        if self.mode == AzarArchiveMode.Read:
            self.stream = open(path, 'rb')
            self.writer_stream = open(out_path, 'w', encoding=ENCODING)
            self.decoder = mode_processor(self.stream, self.writer_stream, progress_callback)
        elif self.mode == AzarArchiveMode.Write:
            self.stream = open(path, 'r', encoding=ENCODING)
            self.writer_stream = open(out_path, 'wb')
            self.encoder = mode_processor(self.stream.read(), self.writer_stream, progress_callback)
        else:
            raise TypeError()

        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mode == AzarArchiveMode.Write:
            self.stream.flush()
        self.stream.close()
        self.writer_stream.close()

    def write(self):
        assert self.mode == AzarArchiveMode.Write

        self.encoder.write()
        if self.finish_callback is not None:
            self.finish_callback()

    def read(self):
        assert self.mode == AzarArchiveMode.Read

        self.decoder.read()
        if self.finish_callback is not None:
            self.finish_callback()

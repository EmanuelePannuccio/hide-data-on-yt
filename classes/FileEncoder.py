from os.path import basename
import hashlib
from os import stat


class FileEncoder:
    MD5_SIZE=32

    def __init__(self, path):
        self.__path = path

    def getPath(self):
        return self.__path

    def _read(self):
        with open(self.__path, "rb") as fp:
            while True:
                chunk = fp.read(4096)
                if not chunk:
                    break

                for b in chunk:
                    yield b
    
    def __encode(self):
        """
        Encode file as binary string in format: filename_bytes_len(1byte)|filename_bytes|md5_bytes|file_content_len(6byte)|file_content
        """
        filename : str = basename(self.__path)
        md5 : str = hashlib.md5(open(self.__path,'rb').read()).hexdigest()
        content = self._read()

        filename_bytes = filename.encode()

        filename_bytes_len = len(filename_bytes)
        filename_bytes_len = filename_bytes_len.to_bytes(1, byteorder="big").ljust(1, b'\0')

        md5_bytes = md5.encode()

        content_len = stat(self.__path).st_size.to_bytes(6, byteorder="big")

        content = self._read()
        
        from itertools import chain
        ba = bytearray(
            chain.from_iterable([
                filename_bytes_len,
                filename_bytes,
                md5_bytes,
                content_len
            ])
        )

        for byte in ba:
            yield byte
            
        for byte in content:
            yield byte
    
    @classmethod
    def encode(cls, path):
        f = FileEncoder(path)
        return f.__encode()
    
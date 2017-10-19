from binascii import hexlify
from io import SEEK_SET
from struct import unpack


class BinaryStream(object):
    def __init__(self, bytes):
        self.bytes = bytes

    def seek(self, offset, whence=SEEK_SET):
        self.bytes.seek(offset, whence)

    def tell(self):
        return self.bytes.tell()

    def read_md5(self):
        """Read MD5 hash.

        Returns
        --------
        hash: bytes.
            Lower case MD5 hash.
        """
        return hexlify(self.bytes.read(16))

    def read_uint32_be(self):
        return unpack('>I', self.bytes.read(4))[0]

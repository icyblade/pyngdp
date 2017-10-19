from binascii import hexlify
from hashlib import md5


class Index(object):
    EMPTY_HASH = b'0' * 32

    def __init__(self, binary_stream):
        """Parser for archive index (.index) files.

        Parameters
        --------
        binary_stream: instance of pyngdp.binary_stream.BinaryStream.
        """
        self.binary_stream = binary_stream
        self.data = None

    def _parse(self):
        """Parse .index file."""
        checksum_size = 8  # initial guess
        file_size = self.binary_stream.bytes.getbuffer().nbytes
        n_chunks = (file_size - 4 - 3 * checksum_size) / 4120
        if int(n_chunks) != n_chunks:
            raise ValueError('Cannot parse index, maybe checksum_size != 8?')
        n_chunks = int(n_chunks)

        # calculate chunk hash
        chunk_hash = []
        self.binary_stream.seek(0)
        for chunk_id in range(n_chunks):
            chunk = self.binary_stream.bytes.read(4096)
            hash = md5(chunk).hexdigest()
            hash = bytes(hash[:16].encode())
            chunk_hash.append(hash)

        # read each chunks
        data = [[] for _ in range(n_chunks)]
        self.binary_stream.seek(0)
        for chunk_id in range(n_chunks):
            hash_id = 0
            while hash_id < 4096 // 24:  # 24 bytes per record, 4096//24=170 entries per chunk
                hash = self.binary_stream.read_md5()
                size = self.binary_stream.read_uint32_be()
                offset = self.binary_stream.read_uint32_be()
                if hash != self.EMPTY_HASH and size != 0 and offset != 0:
                    data[chunk_id].append((hash, size, offset))
                hash_id += 1
            chunk_ending = self.binary_stream.read_md5()
            assert chunk_ending == self.EMPTY_HASH

        # read chunk verification
        last_hash = [i[-1][0] for i in data]
        for i in last_hash:
            assert i == self.binary_stream.read_md5()

        # verify chunk hash
        for correct_hash in chunk_hash[:-1]:  # the last chunk hash is not considered
            inline_hash = hexlify(self.binary_stream.bytes.read(8))
            assert correct_hash == inline_hash

        assert self.binary_stream.tell() + 12 + 3 * checksum_size == file_size

        return [
            (hash.decode(), size, offset)
            for chunk in data
            for hash, size, offset in chunk
        ]

    def get_hashes(self):
        self.data = self._parse()
        return self.data

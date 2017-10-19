def test_init():
    from pyngdp import NGDP

    ngdp = NGDP('wow')
    for _, _ in ngdp.download_cdn_index_file():
        break


def test_get_hash():
    from pyngdp import NGDP

    ngdp = NGDP('wow')
    for _, index in ngdp.download_cdn_index_file():
        hashes = index.get_hashes()
        for hash, size, offset in hashes:
            assert isinstance(hash, str)
            assert len(hash) == 32
            assert isinstance(size, int)
            assert isinstance(offset, int)
        break

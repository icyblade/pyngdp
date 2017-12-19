import pytest


def test_init():
    from pyngdp import NGDP

    NGDP('wow')

    with pytest.raises(NotImplementedError):
        NGDP('titan')

    with pytest.raises(ValueError):
        NGDP('wow', 'Mars')


def test_cdns():
    from pyngdp import NGDP

    ngdp = NGDP('wow')
    assert isinstance(ngdp.cdns, dict)
    assert set(ngdp.cdns.keys()) == {'Name', 'Path', 'Hosts', 'ConfigPath', 'Servers'}


def test_versions():
    from pyngdp import NGDP

    ngdp = NGDP('wow')
    assert isinstance(ngdp.versions, dict)
    assert set(ngdp.versions.keys()) == {
        'Region', 'BuildConfig', 'CDNConfig', 'KeyRing', 'BuildId', 'VersionsName', 'ProductConfig'
    }


def test_build_config():
    from pyngdp import NGDP

    ngdp = NGDP('wow')
    assert isinstance(ngdp.build_config, dict)
    assert set(ngdp.build_config.keys()) == {
        'root', 'install', 'install-size', 'download', 'download-size', 'encoding', 'encoding-size',
        'patch', 'patch-size', 'patch-config', 'build-name', 'build-uid', 'build-product',
        'build-playbuild-installer', 'build-partial-priority'
    }


def test_cdn_config():
    from pyngdp import NGDP

    ngdp = NGDP('wow')
    assert isinstance(ngdp.cdn_config, dict)
    assert set(ngdp.cdn_config.keys()) == {'archives', 'archive-group', 'patch-archives', 'patch-archive-group'}


def test_download_cdn_index_file():
    from pyngdp import NGDP
    from pyngdp.index import Index

    ngdp = NGDP('wow')
    for hash, index in ngdp.download_cdn_index_file():
        assert isinstance(hash, str)
        assert len(hash) == 32
        assert isinstance(index, Index)
        break

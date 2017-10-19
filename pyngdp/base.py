import warnings
from io import StringIO

import pandas as pd

from .index import Index
from .logger import build_logger
from .session import Session


class NGDP(object):
    def __init__(self, program_code, cdn='us'):
        self.logger = build_logger()

        if program_code not in ['wow', 'wow_beta', 'wowt']:
            raise NotImplementedError(f'Program code {program_code} is not implemented yet.')
        if cdn not in ['us', 'cn']:
            raise ValueError(f'Invalid CDN {cdn}')

        self.program_code = program_code
        self.logger.info(f'Using program code: {program_code}.')
        self.cdn = cdn
        self.logger.info(f'Using CDN: {cdn}.')
        self.host = 'http://us.patch.battle.net:1119'
        self.session = Session()

    @property
    def cdns(self):
        text = self.session.get_text(f'{self.host}/{self.program_code}/cdns')
        stringio = StringIO(text)
        df = pd.read_csv(stringio, sep='|')
        for col in df.columns:
            name, type = col.split('!')
            df = df.rename(columns={col: name})
            if type == 'STRING:0':
                df[name] = df[name].astype(str)
            else:  # pragma: no cover
                raise ValueError(f'Invalid type: {type}')

        df['Hosts'] = df['Hosts'].apply(lambda x: x.split(' '))

        if self.cdn in df['Name'].values:
            df = df.query(f'Name=="{self.cdn}"')
        else:  # pragma: no cover
            warnings.warn(f'CDN {self.cdn} not found, using us.')
            df = df.query(f'Name=="us"')

        assert len(df) == 1
        data = df.iloc[0].to_dict()
        self.logger.info(f'{len(data["Hosts"])} hosts found: {data["Hosts"]}.')

        return data

    @property
    def versions(self):
        text = self.session.get_text(f'{self.host}/{self.program_code}/versions')
        stringio = StringIO(text)
        df = pd.read_csv(stringio, sep='|')
        for col in df.columns:
            name, type = col.split('!')
            df = df.rename(columns={col: name})
            if type == 'STRING:0':
                df[name] = df[name].astype(str)
            elif type == 'String:0':
                df[name] = df[name].astype(str)
            elif type == 'HEX:16':
                df[name] = df[name].astype(str)
            elif type == 'DEC:4':
                df[name] = df[name].astype(int)
            else:  # pragma: no cover
                raise ValueError(f'Invalid type: "{type}"')

        if self.cdn in df['Region'].values:
            df = df.query(f'Region=="{self.cdn}"')
        else:  # pragma: no cover
            warnings.warn(f'Region "{self.cdn}" not found, using "us".')
            df = df.query(f'Region=="us"')

        assert len(df) == 1
        data = df.iloc[0].to_dict()
        self.logger.info(f'Version {data["VersionsName"]} found.')

        return data

    def get_cdn_host(self):
        from random import randint
        index = randint(0, len(self.cdns['Hosts']) - 1)
        return self.cdns['Hosts'][index]  # TODO: network test

    @property
    def build_config(self):
        host = self.get_cdn_host()
        self.logger.info(f'Using host: {host}')
        config_path = 'tpr/wow'  # TODO
        hash = self.versions['BuildConfig']
        text = self.session.get_text(f'http://{host}/{config_path}/config/{hash[:2]}/{hash[2:4]}/{hash}')

        data = {}
        for line in text.splitlines():
            if line.startswith('#') or not line:
                continue
            unpack = line.split(' = ')
            assert len(unpack) == 2, line
            key, value = unpack
            data[key] = value.split(' ')

        return data

    @property
    def cdn_config(self):
        host = self.get_cdn_host()
        config_path = 'tpr/wow'  # TODO
        hash = self.versions['CDNConfig']
        text = self.session.get_text(f'http://{host}/{config_path}/config/{hash[:2]}/{hash[2:4]}/{hash}')

        data = {}
        for line in text.splitlines():
            if line.startswith('#') or not line:
                continue
            unpack = line.split(' = ')
            assert len(unpack) == 2, line
            key, value = unpack
            data[key] = value.split(' ')

        return data

    def download_cdn_index_file(self):
        host = self.get_cdn_host()
        config_path = 'tpr/wow'  # TODO
        for hash in self.cdn_config['archives']:
            binary = self.session.get_binary(f'http://{host}/{config_path}/data/{hash[:2]}/{hash[2:4]}/{hash}.index')
            yield hash, Index(binary)

from typing import List
import argparse
from os import environ
from pathlib import Path


POSTGRES_DSN = 'dbname=postgres user=postgres password=postgres host=172.17.0.1'
POSTGRES_FETCHMANY_ARRAYSIZE = 10

BASE_DIR = Path(__file__).parent
FIXTURES_DIR = BASE_DIR / 'fixtures'
UPLOADS_DIR = Path('/var/kt_images')

def env(key: str, default: str):
    return environ.get(key, default)

def postgres_dsn(parser: argparse.ArgumentParser):
    parser.add_argument('--postgres_dsn', dest='pg_dsn', type=str,
      help='postgres data source name',
      default=env('POSTGRES_DSN', POSTGRES_DSN))

def postgres_arraysize(parser: argparse.ArgumentParser):
    parser.add_argument('--postgres_arraysize', dest='pg_arraysize', type=int,
            help='postgres chunk arraysize',
            default=env('POSTGRES_FETCHMANY_ARRAYSIZE',
                        POSTGRES_FETCHMANY_ARRAYSIZE))

def api_endpoint(parser: argparse.ArgumentParser):
        parser.add_argument('--host', dest='host', type=str,
            help='host address, default: 0.0.0.0',
            default=env('KT_IMAGES_DEMO_HOST',
                        '0.0.0.0'))

        parser.add_argument('--port', dest='port', type=int,
            help='port, default: 8080',
            default=env('KT_IMAGES_DEMO_PORT',
                        8080))

def uploads_dir(parser: argparse.ArgumentParser):
    parser.add_argument('--uploads_dir', dest='uploads_dir', type=Path,
      help='image uploads',
      default=env('KT_IMAGES_UPLOAD_DIR', UPLOADS_DIR))


class BaseSettings:
    """
    Base Command line arguments parser, defaults are taken from env
    vars (in flavour of Docker) or consts
    """
    host: str
    port: int
    pg_dsn: str
    pg_arraysize: int
    uploads_dir: str
    parser: argparse.ArgumentParser
    app_description: str = None
    app_settings = (postgres_dsn, )
    
    def __init__(self, params: List[str] = None):
        parser = self.parser = argparse.ArgumentParser(
            description=self.app_description)

        for func in self.app_settings:
            func(parser) 

        args = parser.parse_args(params or tuple())
        for k in args.__dict__.keys():
            setattr(self, k, args.__dict__[k])

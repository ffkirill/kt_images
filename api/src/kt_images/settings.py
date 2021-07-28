import argparse
from os import environ


POSTGRES_DSN = 'dbname=postgres user=postgres password=postgres host=172.17.0.1'


def env(key: str, default: str):
    return environ.get(key, default)


class Settings:
    """
    Command line arguments parser, defaults are taken from env
    vars (in flavour of Docker) or consts
    """
    host: str
    port: int
    postgres_dsn: str
    
    def __init__(self, argv):
        parser = argparse.ArgumentParser(description='Images http storage backend.')

        parser.add_argument('--host', dest='host', type=str,
            help='host address, default: 0.0.0.0',
            default=env('KT_IMAGES_DEMO_HOST',
                        '0.0.0.0'))

        parser.add_argument('--port', dest='port', type=int,
            help='port, default: 8080',
            default=env('KT_IMAGES_DEMO_PORT',
                        8080))

        parser.add_argument('--postgres_dsn', dest='postgres_dsn', type=str,
            help='postgres data source name',
            default=env('POSTGRES_DSN',
                        POSTGRES_DSN))

        args = parser.parse_args(argv)
        for k in args.__dict__.keys():
            setattr(self, k, args.__dict__[k])

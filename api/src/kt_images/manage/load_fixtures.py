from typing import List

from pathlib import Path
import stat
import argparse
import sys
import kt_images.base_settings as settings
import psycopg2
from kt_images.base_settings import FIXTURES_DIR


def fixture_names_param(parser: argparse.ArgumentParser):
    parser.add_argument('fixtures', nargs='*',
        default=tuple(),
        help="fixtures list")

def list_all_fixtures(parser: argparse.ArgumentParser):
    parser.add_argument('--list_all', dest='list_fixtures', action='store_true',
      help='list all fixtures',
      default=False)

def load_all_fixtures(parser: argparse.ArgumentParser):
    parser.add_argument('--apply_all', dest='apply_all', action='store_true',
      help='apply all fixtures',
      default=False)

class Settings(settings.BaseSettings):
    app_description = "Load fixtures. !DANGEROUS, applies DDL to database!"
    app_settings = (settings.postgres_dsn,
        list_all_fixtures,
        load_all_fixtures,
        fixture_names_param)
    fixtures: List[str]
    list_fixtures: bool = False
    apply_all: bool = False

def get_fixtures() -> List[Path]:
    """Returns fixtures files generator"""
    return sorted((path
        for path in Path(FIXTURES_DIR).iterdir()
        if path.is_file() and path.stat().st_mode & stat.S_IEXEC),
        key=lambda path:path.name
    )


def main(argv):
    config = Settings(argv)
    
    # Just list fixtures
    if config.list_fixtures:
        print([path.name for path in get_fixtures()])
        return
    
    # Apply fixtures
    fixtures: List[Path] = []
    if config.apply_all:
        fixtures = get_fixtures()
    elif config.fixtures:
        fixtures = [Path(FIXTURES_DIR) / name for name in config.fixtures]
    
    conn = psycopg2.connect(config.pg_dsn)
    cur = conn.cursor()
    for fixture in fixtures:
        with fixture.open('r') as file:
            sql = ''.join(file.readlines())
            cur.execute(sql)
            print(sql)
    
    print(f'Applied {len(fixtures)} fixtures.')
    

if __name__ == '__main__':
    main(sys.argv[1:])

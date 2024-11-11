from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
import yaml
import os


def get_engine(is_debug: bool = False) -> Engine:
    secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.yaml')
    with open(secrets_path) as file:
        secrets = yaml.safe_load(file)
        if is_debug:
            return create_engine(secrets['sqlalchemy_connection_string_qa'], echo=True)
        else:
            return create_engine(secrets['sqlalchemy_connection_string'], echo=True)


def get_session(is_debug: bool = False) -> scoped_session[Session]:
    engine = get_engine(is_debug)
    return scoped_session(sessionmaker(bind=engine))

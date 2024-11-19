from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
import yaml
import os


def set_engine_for_ctx(debug: bool) -> Engine:
    secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.yaml')
    with open(secrets_path) as file:
        secrets = yaml.safe_load(file)
        if debug:
            return create_engine(secrets['sqlalchemy_connection_string_qa'], echo=True)
        else:
            return create_engine(secrets['sqlalchemy_connection_string'], echo=True)

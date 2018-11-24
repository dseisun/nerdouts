from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import yaml


def get_connection(is_debug):
    with open('secrets.yaml') as file:
        secrets = yaml.load(file)
        if is_debug:
            engine = create_engine(secrets['sqlalchemy_connection_string_qa'], echo=True)
        else:
            engine = create_engine(secrets['sqlalchemy_connection_string'], echo=True)

    return scoped_session(sessionmaker(bind=engine))

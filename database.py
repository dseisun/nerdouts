from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import yaml


with open('secrets.yaml') as file:
    secrets = yaml.load(file)
    engine = create_engine(secrets['sqlalchemy_connection_string'], echo=True)

Session = scoped_session(sessionmaker(bind=engine))

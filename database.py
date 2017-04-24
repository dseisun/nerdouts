from sqlalchemy import create_engine
import yaml


with open('secrets.yaml') as file:
    secrets = yaml.load(file)
    engine = create_engine(secrets['sqlalchemy_connection_string'], echo=True)

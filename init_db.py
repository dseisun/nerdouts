from models import Base
from workout import engine


if __name__ == "__main__":
    Base.metadata.create_all(engine)

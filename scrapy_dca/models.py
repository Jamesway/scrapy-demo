from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from scrapy.utils.project import get_project_settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))

def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class PhysicianDB(DeclarativeBase):
    __tablename__ = 'physician_table'

    id = Column(String(36), primary_key = True)
    license = Column('license', String(32), index = True, unique = True)
    physician_name = Column('name', String(60))
    license_type = Column('license_type', String(32))
    address = Column('address', Text)
    services = Column('services', Text)
    enabled = Column('enabled', Boolean, index = True, default = True)
    scraped_at = Column('scraped_at', DateTime)


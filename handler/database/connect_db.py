from sqlalchemy import create_engine

from config import settings

engine = create_engine(settings.POSTGRESS_DATABASE_URL)

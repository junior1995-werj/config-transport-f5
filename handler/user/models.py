from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):

    __tablename__ = "big_ip_user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String())
    username = Column(String(), unique=True)
    password = Column(String())
    status = Column(String())

    def __init__(self, name, username, password, status):
        self.name = name
        self.username = username
        self.password = password
        self.status = status

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

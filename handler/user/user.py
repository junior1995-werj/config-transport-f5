from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from handler.user.models import UserModel
from handler.database.connect_db import engine


class User:
    def __init__(self):
        self.session = sessionmaker(bind=engine)

    def create_user(self, name, username, password):
        sessao = self.session()
        sessao.add(
            UserModel(
                name=name,
                username=username,
                password=generate_password_hash(password, method="sha256"),
                status=True,
            )
        )
        sessao.commit()
        sessao.close()

    def get_user(self, username):
        sessao = self.session()
        user = sessao.query(UserModel).filter(UserModel.username == username).first()
        return user

    def load_user_get_by_id(self, user_id):
        sessao = self.session()
        user = sessao.query(UserModel).filter(UserModel.id == user_id).first()
        return user

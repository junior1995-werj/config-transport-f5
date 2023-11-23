from prettyconf import config


class Settings:
    POSTGRESS_DATABASE_URL = config("POSTGRESS_DATABASE_URL", default="")
    SERVER_SOCKET = config("SERVER_SOCKET", default="127.0.0.1:5000")
    UPLOAD_FOLDER = config("UPLOAD_FOLDER", default="handler/big_ip/files")


settings = Settings()

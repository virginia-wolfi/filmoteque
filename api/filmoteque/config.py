
class Config(object):
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False
    SECRET_KEY = '20d59e04e26833e150ee3da1ea0f175905685e91'


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:8066@localhost/film_collection'

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:8066@localhost/film_collection_test'
    TESTING = True




import os
import pymysql


class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = "SECRET_KEY"

    APP_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(APP_DIR)
    VAR_DIR = ROOT_DIR + '/var/'

    # SQLALCHEMY_DATABASE_URI = 'sqlite:///../test.db'
    HOSTNAME = '127.0.0.1'
    PORT = '3306'
    DATABASE = 'resale_test'
    USERNAME = 'root'
    PASSWORD = 'root'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

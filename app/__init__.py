from flask import Flask

app = Flask(__name__)

from flask_redis import FlaskRedis

redis_client = FlaskRedis(app)

from app import routes
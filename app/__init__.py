from flask import Flask
import redis

app = Flask(__name__)

# from flask_redis import FlaskRedis

# app.config['REDIS_URL'] = "redis://redis:6379/0"

# redis_client = FlaskRedis(app)

redis_client = redis.Redis(host='redis', port=6379)

from app import routes


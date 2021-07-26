from flask import Flask
import redis
import os

app = Flask(__name__)

redis_client = redis.Redis(host=os.environ['REDIS_HOST'], port=6379)

from app import routes


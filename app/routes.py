from app import app
from flask import request, make_response
from app import redis_client

import requests
import json
import os
from datetime import timedelta

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


# returns average temp
@app.route('/gettemp', methods=['GET'])
def gettemp():

    # get args
    r_json = request.args

    # check for lat/long
    if r_json['lat'] and r_json['long']:
        lat = r_json['lat']
        long = r_json['long']

        coordinates = "({0}, {1})".format(lat, long)

        # check cache
        cache_data = get_data(key=coordinates)

        if cache_data is not None:
            data = json.loads(cache_data)
            data['cache'] = True

            resp = make_response(data)
            resp.headers['X-Cached-Temp'] = True
            return resp

        else:
            # get current temps
            temp = returnAvgTemp(lat, long)

            # build json response
            data = {}
            loc1 = {}

            loc1['lat'] = lat
            loc1['long'] = long
            loc1['currentTemp'] = temp

            data['loc1'] = loc1
            data['cache'] = False

            # cache data
            data = json.dumps(data)
            state = set_data(key=coordinates, value=data, timeout=os.environ['TIMEOUT'])

            print(state)

            # sets up return 
            resp = make_response(json.loads(data))
            resp.headers['X-Cached-Temp'] = False
            return resp


def getOpenWeatherAPI(lat, long):
    print("Getting openWeatherAPI temp for {0}, {1}".format(lat, long))

    r = requests.get('http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}&units={3}'.format(
        lat,
        long,
        os.environ['APIKEY'],
        'imperial'
    ))
    
    main = r.json()['main']['temp']
    return str(main)


def getWeatherGovTemp(lat, long):
    print("Getting weatherGov temp for {0}, {1}".format(lat, long))
    
    r = requests.get('https://api.weather.gov/points/{0},{1}/forecast'.format(lat, long))
    
    periods = r.json()['properties']['periods']

    # locates todays temp forecast
    for i in periods:
        if i['name'] == 'Today':
            temp =  i['temperature']

    return str(temp)
    

# returns avg temp
def returnAvgTemp(lat, long):
    gov = getWeatherGovTemp(lat, long)
    open = getOpenWeatherAPI(lat, long)

    return str((float(gov) + float(open)) / 2)


# get data from redis
def get_data(key):
    val = redis_client.get(key)
    return val

# set data to redis
def set_data(key, value, timeout):
    state = redis_client.setex(key, timedelta(seconds=int(timeout)), value=value, )
    return state


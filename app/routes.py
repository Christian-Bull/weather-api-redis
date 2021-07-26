from app import app, redis_client
from flask import request, make_response

import requests
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

        temp, cached = returnAvgTemp(lat, long)

        # build json response
        data = {}
        loc1 = {}

        loc1['lat'] = lat
        loc1['long'] = long
        loc1['currentTemp'] = temp

        data['loc1'] = loc1

        # setup response
        resp = make_response(data)

        # checks if either response was a cached response
        if cached:
            resp.headers['X-Cached-Temp'] = True
        else:
            resp.headers['X-Cached-Temp'] = False

        return resp
    else:
        return "please provide a valid lat/long"


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
        if i['number'] == 1:
            temp =  i['temperature']

    return str(temp)
    

# returns avg temp
def returnAvgTemp(lat, long):
    cache_flag = 0
    coordinates = "({0}, {1})".format(lat, long)

    # checks gov api for cached response
    govKey = "gov-{0}".format(coordinates)
    govCache = get_data(key=govKey)

    if govCache is not None:
        govData = govCache
        cache_flag = 1
    else:
        govData = getWeatherGovTemp(lat, long)
        govState = set_data(key=govKey, value=govData, timeout=os.environ['GOVTIMEOUT'])
        print(govState)

    # checks for openweather cached response
    openKey = "open-{0}".format(coordinates)
    openCache = get_data(key=openKey)

    if openCache is not None:
        openData = openCache
        cache_flag = 1
    else:
        openData = getOpenWeatherAPI(lat, long)
        openState = set_data(key=openKey, value=openData, timeout=os.environ['OPENTIMEOUT'])
        print(openState)

    return str((float(govData) + float(openData)) / 2), cache_flag


# get data from redis
def get_data(key):
    val = redis_client.get(key)
    return val

# set data to redis
def set_data(key, value, timeout):
    state = redis_client.setex(key, timedelta(seconds=int(timeout)), value=value, )
    return state


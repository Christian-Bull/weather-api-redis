# weather-api-redis

Simple weather api that takes the average temp of multiple sources

Uses redis for caching api calls to minimize repeated calls to temp sources. Each source updates the current temp at different intervals, thus repeated requests to the same source generally results in redundent info returned.

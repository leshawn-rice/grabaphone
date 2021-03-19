# Grabaphone!

[![Build Status](https://travis-ci.com/leshawn-rice/grabaphone.svg?branch=main)](https://travis-ci.com/leshawn-rice/grabaphone) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![GitHub issues open](https://img.shields.io/github/issues/leshawn-rice/grabaphone)](https://github.com/leshawn-rice/grabaphone/issues)

Grabaphone is a RESTful API that provides developers with data about cellular devices such as smartphones, flip-phones, tablets etc.

Grabaphone contains data on over 5000 devices, each with up to 60 data points. Data is sent and received as JSON. 

## Built With

Language: Python 3.8.5

Web Framework: Flask w/ SQLAlchemy

Database: PostgreSQL

## Features

Name: Manufacturers & devices can be filtered by name

Release Date: Devices can be filterd by release date

 - Latest: The latest devices that have come out
 - Released: Only released devices
 - Coming Soon: Oldest and non-released

**Coming Soon**: More filtering options, including filter by specs

## Data

Manufacturers:

 - ID
 - Name
 - URL (links to phonearena.com)
 - Image URL

Devices:

 - ID
 - Manufacturer
 - Name
 - Rating
 - Release Date
 - Image URL
 - Device URL
 - Specs

Specs:

 - ID
 - Category (Display, Buyers information, Hardware etc.)
 - Name (Size, Price, Dimensions etc.) **Currently the names include a semicolon at the end
 - Description (6.7 inches, $500, 5in x 1in x 0.5in etc.)

## How To Use

1. Go to [The API](https://grabaphone.herokuapp.com) and get an API Key for free (on heroku, will take a moment to spin up)
2. Send a request to your desired route with any necessary filtering
    - For example send the following payload:
    
        ```{'key': '1234APIKey', 'name': 'iPhone', 'limit': 50, 'is_released': true}```
    
    - To https://grabaphone.herokuapp.com/api/get-latest, and you will receive the 50 latest released devices with 'iPhone' in their name

## Demo

There is a [Live Demo](https://grabaphone.surge.sh) on how you might utilize this API

## Credits

This API was inspired by [FonoAPI](https://github.com/shakee93/fonoapi).

All manufacturer and device data was scraped from [Phonearena](https://phonearena.com)

## Going live by the end of March 2021!
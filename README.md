# VUBIX

![screenshot](screenshot.png)

## What's this ?

Just try to pronounce the concatenation of `VUB` and `ICS`. You got it.

## Installation
    
    * Installer PostgreSQL (database : vubix, user : vubix, password : vubix) 


    virtualenv ve
    source ve/bin/activate
    pip install -r requirements.txt

## Startup
    
    ./manage.py migrate
    ./manage.py reload_courses

## Running
    
    ./manage.py runserver

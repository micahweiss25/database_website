#!/usr/bin/python3

from sys import path

path.insert(0, '/var/www/flask/')
from app import app as application

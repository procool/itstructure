#! /usr/bin/env python2
# encoding: utf8

import py_path
from utils.db import create_all, _database


if __name__ == "__main__":
    if not raw_input("Are you shure you want to create database?[yes/no]: ") == 'yes':
        exit(0)

    print "Creating database with default alias in global settings..."

    ## Init session
    session = _database._get_db_session()

    ## Import and create all models:
    create_all(dirpath='models')



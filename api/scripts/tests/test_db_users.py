#! /usr/bin/env python2
# encoding: utf8

import py_path
from utils.db import get_db_session
from models.users.sa_models import Users, UsersExtra, UsersContacts


if __name__ == "__main__":

    ## Init session
    session = get_db_session(echo=True)

    ## Test models:
    print session.query(Users).first()
    print session.query(UsersExtra).first()
    print session.query(UsersContacts).first()




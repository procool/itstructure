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

    ## remove all:
    #print "REMOVING@!!!"
    #print session.using_bind('master').query(Users).delete()
    #print "<<<REMOVING@!!!"

    ## Get clear list:
    #print session.query(Users).all()

    ## Create an element:
    #tt = TestModel(name='test1')
    #session.add(tt)
    #tt = TestModel(name='test2')
    #session.add(tt)

    #session.commit()

    ## Get all new elements:
    #print session.query(TestModel).all()



#! /usr/bin/env python2
# encoding: utf8

import py_path
from utils.db import get_db_session
from models.addresses.sa_models import Address
from models.partners.sa_models import Partner



if __name__ == "__main__":

    ## Init session
    session = get_db_session(echo=True)

    ## Get list:
    print session.query(Partner).all()

    ## remove all:
    print "REMOVING@!!!"
    print session.using_bind('master').query(Partner).delete()
    print session.using_bind('master').query(Address).delete()
    print "<<<REMOVING@!!!"

    ## Get clear list:
    print session.query(Partner).all()

    ## Create an element:
    addr = Address('50.2233_37.332255', 'some address', '{}')
    session.add(addr)
    session.commit()
    print "New addr id:", addr.id
    partner = Partner('Test partner', 'moscow', addr.id)
    session.add(partner)
    session.commit()

    ## Get all new elements:
    for partner in session.query(Partner).all():
        print partner.name
        print partner.address, partner.address.address_string



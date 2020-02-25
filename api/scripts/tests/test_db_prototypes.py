#! /usr/bin/env python2
# encoding: utf8

import unittest

import py_path
from libs.db import get_db_session
from models.prototypes.sa_models import Prototypes, ProtoObjects, Layouts, LayoutProtos
from models.prototypes.sa_models import LayoutDiscuss, LayoutDiscussObjects, LayoutUsers, LayoutUsersAccess


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        ## Init session
        self.dbsess = get_db_session(echo=True)

    def test_Prototypes(self):
        self.assertIsInstance(self.dbsess.query(Prototypes).count(), long)

    def test_ProtoObjects(self):
        self.assertIsInstance(self.dbsess.query(ProtoObjects).count(), long)

    def test_Layouts(self):
        self.assertIsInstance(self.dbsess.query(Layouts).count(), long)

    def test_LayoutProtos(self):
        self.assertIsInstance(self.dbsess.query(LayoutProtos).count(), long)

    def test_LayoutDiscuss(self):
        self.assertIsInstance(self.dbsess.query(LayoutDiscuss).count(), long)

    def test_LayoutDiscussObjects(self):
        self.assertIsInstance(self.dbsess.query(LayoutDiscussObjects).count(), long)

    def test_LayoutUsers(self):
        self.assertIsInstance(self.dbsess.query(LayoutUsers).count(), long)

    def test_LayoutUsersAccess(self):
        self.assertIsInstance(self.dbsess.query(LayoutUsersAccess).count(), long)

    ##def test_(self):
    ##    self.assertIsInstance(self.dbsess.query().count(), long)



if __name__ == '__main__':
    unittest.main()

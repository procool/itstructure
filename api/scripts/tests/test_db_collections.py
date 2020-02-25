#! /usr/bin/env python2
# encoding: utf8

import unittest

import py_path
from libs.db import get_db_session
from models.collections.sa_models import Categories, Objects, ObjectsCategories


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        ## Init session
        self.dbsess = get_db_session(echo=True)

    def test_categories(self):
        self.assertIsInstance(self.dbsess.query(Categories).count(), long)

    def test_objects(self):
        self.assertIsInstance(self.dbsess.query(Objects).count(), long)

    def test_objects_categories(self):
        self.assertIsInstance(self.dbsess.query(ObjectsCategories).count(), long)



if __name__ == '__main__':
    unittest.main()

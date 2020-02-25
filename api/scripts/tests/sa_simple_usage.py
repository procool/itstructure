#! /usr/bin/env python2
# encoding: utf8

## импортируем пути что бы видеть globals/
import py_path

# Движек работы с базой, get_db_session вернет созданную сессию:
from utils.db import get_db_session

# Наша модель:
from models.testmodel.sa_models import Test as TestModel


if __name__ == "__main__":

    ## Получим сессию:
    session = get_db_session(echo=True)

    ## Выведем все записи из TestModel (используется slave):
    # print session.query(TestModel).all()
    lll = session.query(TestModel).all()
    # lll = session.query(TestModel).filter(TestModel.name=='test1')
    # lll = session.query(TestModel.id).scalar()
    print(type(lll[0]))
    print(lll)
    print(lll[0].name)
    for instance in lll:
        print(instance.name, instance.descr)

    ## Используя "master" удалим все записи:
    print session.using_bind('master').query(TestModel).delete()
    ## using_bind возвращает себя(Session), и ставит настройку 
    ## - при следующем запросе(query в той же строке) использовать "master";
    ## после использования query настройка сбрасывается, и сессии работают 
    ## по автоопредилению

    ## Создадим пару элементов (используется master):
    tt = TestModel(name='test1', descr='descr1')
    session.add(tt)
    tt = TestModel(name='test2', descr='descr2')
    session.add(tt)
    session.commit()
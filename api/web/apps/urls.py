from flaskcbv.url import Url, include, make_urls

import index.urls
import app_tests.urls
import auth.urls
import collections_app.urls

namespases = make_urls(
    Url('/', include(index.urls.namespases, namespace='index')),
    Url('/tests', include(app_tests.urls.namespases, namespace='tests', description='Simple Tests')),
    Url('/auth', include(auth.urls.namespases, namespace='auth', description='Authorization')),
    Url('/collections', include(collections_app.urls.namespases, namespace='collections', description='Collections')),
)


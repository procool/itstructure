from flaskcbv.url import Url, make_urls
from views import jsonView, errorView
#from views import authedView

namespases = make_urls(
    Url('/json', jsonView(), name="json"),
    Url('/error', errorView(), name="error"),
    #Url('/session', sessionView(), name="session"),
    #Url('/isauthed', authedView(), name="isauthed"),
)




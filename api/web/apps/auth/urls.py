from flaskcbv.url import Url, make_urls
from views import authView, sessionView

namespases = make_urls(
    Url('/', authView(), name="auth"),
    Url('/session/', sessionView(), name="session"),
    #Url('logout/', logOutView(), name="logout"),
)




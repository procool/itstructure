from flaskcbv.url import Url, make_urls
from views import mainView, mainHandlersView

namespases = make_urls(
    Url('', mainView(), name="main"),
    Url('handlers/', mainHandlersView(), name="handlers"),
)




from flask import url_for
from flaskcbv.view import View
from misc.mixins import HelperMixin
from misc.views import JSONView



class mainView(HelperMixin, View):

    def helper(self):
        return """
JSON API Helper
===============

If you want to get a help page, use helper=true(or 1/y) in query parameters of GET request;
For example, if you would like to read help page of some handler, use:
/HANDLER/?helper=1
Use: "%(handlers)s" url to get the list of public handlers (use helper=1 for human readable)

NOTE: Most of handlers are need user's session, you should get it by the passport project;

In this case, you should use "session" query argument to get the full list of handlers allowed for you: 
%(handlers)s?session=<your_session>&helper=1

WARNING!!! In current development mode, the list of all handlers is visible for everybody!

        """ % { "handlers": url_for('index:handlers'), }

    def dispatch(self, request, *args, **kwargs):
        return self.helper_response()




class mainHandlersView(JSONView):

    description = "avalible handlers"


    def helper(self):
        r = """\nAvalible handlers list(for this user):\n"""

        descriptions = {}
        namespaces = {}
        max_url_len = 0
        for url_, def_ in self.get_all_urls(with_defs=True).items():
            #if not self.request.user.has_permission(url_):
            #    continue

            try: url = def_.url
            except:
                try: url = def_.__self__.url
                except: continue

            try: descr_ = def_.description
            except:
                try: descr_ = def_.view_class.description
                except: 
                    try: descr_ = def_.__self__.description
                    except: descr_ = ''

            if hasattr(descr_, '__call__'):
                descr_ = descr_()

            descriptions[url.url] = descr_
            if max_url_len <  len(url.url):
                max_url_len = len(url.url)


            if not url.namespace in namespaces:
                namespaces[url.namespace] = (url.namespace_descr, [])
            namespaces[url.namespace][1].append(url)


        for ns_ in namespaces:
            ns_descr = namespaces[ns_][0]
            urls = namespaces[ns_][1]

            r += "\n%s:\n" % ns_descr
            for url_ in urls:
                r += "	%s" % url_.url
                r += ''.join(" " for _ in xrange(max_url_len-len(url_.url)))
                r += "	%s\n" % descriptions[url_.url]

        r += "\n"

        return r


    
    def get_context_data(self, **kwargs):
        context = super(mainHandlersView, self).get_context_data(**kwargs)
        context['handlers'] = list()

        for url_, def_ in self.get_all_urls(with_defs=True).items():
            #if not self.request.user.has_permission(url_):
            #    continue

            try: url = def_.url
            except:
                try: url = def_.__self__.url
                except: continue
            context['handlers'].append([url.namespace, url.name, url.url])

        return context

            




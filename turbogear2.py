from wsgiref.simple_server import make_server
from tg import expose, TGController, AppConfig
from CheckAircrewProgram import *
import webhelpers2
import webhelpers2.text

class RootController(TGController):
    @expose()
    def index(self):
        res = test()
        return str(res)
        #return 'Hello World'

    ''' @expose('hello.xhtml')
    def hello(self, person=None):
        return dict(person=person) '''

config = AppConfig(minimal=True, root_controller=RootController())
config.renderers = ['kajiki']
config['helpers'] = webhelpers2
application = config.make_wsgi_app()

print("Serving on port 8080...")
httpd = make_server('', 8080, config.make_wsgi_app())
httpd.serve_forever()
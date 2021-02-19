import bokeh.plotting
import bokeh.application.application
import bokeh.document.document
import bokeh.util.callback_manager
import contextvars
import tornado.web

def on_session_created(self, *callbacks):
    if not hasattr(self, "_session_created_callbacks"):
        self._session_created_callbacks = set()
    for callback in callbacks:
        bokeh.util.callback_manager._check_callback(callback, ('session_context',))
        self._session_created_callbacks.add(callback)
        if self.session_context is not None:
            callback(self.session_context)
bokeh.document.document.Document.on_session_created = on_session_created

old_on_session_created = bokeh.application.application.Application.on_session_created
async def on_session_created(self, session_context):
    await old_on_session_created(self, session_context)
    doc = session_context._document
    if hasattr(doc, "_session_created_callbacks"):
        for callback in doc._session_created_callbacks:
            await callback(session_context)
    return None
bokeh.application.application.Application.on_session_created = on_session_created


def current_bokeh_tornado_server(doc = None):
    """Returns the current bokeh.server.tornado.BokehTornado instance, or
    the one associated with a particular bokeh Document"""
    if doc is None:
        doc = bokeh.plotting.curdoc()
    host = doc.session_context.request.headers["Host"]
    doc_port = None
    if ":" in host:
        doc_port = int(host.split(":")[-1])
    for s, handler in doc.session_context.server_context.application_context.io_loop.handlers.values():
        if not hasattr(s, "getsockname"): continue
        if doc_port is not None and s.getsockname()[1] != doc_port: continue
        connection_handler = handler.__closure__[0].cell_contents # tornado.httpserver.HTTPServer._handle_connection
        http_server = connection_handler.__self__                 # tornado.httpserver.HTTPServer
        bokeh_tornado = http_server.request_callback              # bokeh.server.tornado.BokehTornado
        return bokeh_tornado

class HTTPModel(object):
    def _attach_document(self, doc):
        try:
            return super(HTTPModel, self)._attach_document(doc)
        finally:
            doc.on_session_created(self.on_session_created)

    def on_session_created(self, session_context):
        print("HTTPModel.on_session_created", self)
        self._http_init()

    @property
    def bokeh_tornado(self):
        return self._bokeh_tornado

    @property
    def base_url(self):
        headers = self.document.session_context.request.headers
        host = headers["Host"]
        origin = None
        if "Origin" in headers:
            origin = headers["Origin"].split("://")[-1]
        if origin is None or origin == host:
            return ""
        return "http://%s" % (host,)
    
    def _http_init(self):
        if self.document.session_context is not None and not hasattr(self, "_bokeh_tornado"):
            self._bokeh_tornado = current_bokeh_tornado_server(self.document)
            self.http_init()
            
    def http_init(self):
        pass

current_request = contextvars.ContextVar('current_request')

old_execute = tornado.web.RequestHandler._execute
async def _execute(self, *arg, **kw):
    current_request.set(self.request)
    await old_execute(self, *arg, **kw)
tornado.web.RequestHandler._execute = _execute

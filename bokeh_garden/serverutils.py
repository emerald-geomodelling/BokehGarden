import bokeh.plotting

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
    def properties_with_values(self, include_defaults):
        self._http_init()
        return super(HTTPModel, self).properties_with_values(include_defaults)

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

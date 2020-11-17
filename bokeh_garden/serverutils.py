import bokeh.plotting

def current_bokeh_tornado_server(doc = None):
    """Returns the current bokeh.server.tornado.BokehTornado instance, or
    the one associated with a particular bokeh Document"""
    if doc is None:
        doc = bokeh.plotting.curdoc()
    doc_port = int(doc.session_context.request.headers["Host"].split(":")[-1])
    for s, handler in doc.session_context.server_context.application_context.io_loop.handlers.values():
        if not hasattr(s, "getsockname"): continue
        if s.getsockname()[1] != doc_port: continue
        connection_handler = handler.__closure__[0].cell_contents # tornado.httpserver.HTTPServer._handle_connection
        http_server = connection_handler.__self__                 # tornado.httpserver.HTTPServer
        bokeh_tornado = http_server.request_callback              # bokeh.server.tornado.BokehTornado
        return bokeh_tornado
        #return handler.__closure__[0].cell_contents.__self__.request_callback

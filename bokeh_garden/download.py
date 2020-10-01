import tornado.ioloop
import tornado.web
import socket
import bokeh.layouts
import tornado.web
import tornado.ioloop
import bokeh.core.properties
import weakref
import uuid
import sys

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        download_id = self.request.path.split("/")[-1]
        if download_id in downloads:
            downloads[download_id].get(self)
        else:
            self.set_status(404, "Unknown download ID %s (existing: %s)" % (download_id, ",".join(str(key) for key in downloads.keys())))

app = tornado.web.Application([
    (r"/.*", MainHandler),
])

if hasattr(sys, "_bokeh_garden_download_port"):
    loop = tornado.ioloop.IOLoop.current()
    for fd, (sock, handler) in list(loop.handlers.items()):
        try:
            if isinstance(sock, socket.socket) and sock.getsockname()[1] == sys._bokeh_garden_download_port:
                loop.close_fd(fd)
                loop.remove_handler(fd)
        except:
            loop.remove_handler(fd)

sys._bokeh_garden_download_port = 8912
for attempt in range(100):
    try:
        app.listen(sys._bokeh_garden_download_port)
    except:
        sys._bokeh_garden_download_port += 1
    else:
        break
    
downloads = weakref.WeakValueDictionary()

class Download(bokeh.models.Div):
    __view_model__ = bokeh.models.Div.__view_model__
    __view_module__ = bokeh.models.Div.__view_module__
    __subtype__ = "Download"

    content = bokeh.core.properties.Any(serialized=False)
    filename = bokeh.core.properties.String(default="file.txt", serialized=False)

    def __init__(self, **kw):
        self._download_id = str(uuid.uuid4())
        downloads[self._download_id] = self
        
        bokeh.models.Div.__init__(self, **kw)
        self.text = "<a href='http://localhost:8912/%s' target='_new'>%s</a>" % (self._download_id, self.text)

    def get(self, request_handler):
        request_handler.add_header("Content-Disposition", 'attachment; filename="%s"' % self.filename)
        request_handler.write(bytes(self.content))

import tornado.ioloop
import tornado.web
import socket
import bokeh.layouts
import tornado.web
import tornado.ioloop
import bokeh.plotting
import bokeh.core.properties
import weakref
import uuid
import sys
from . import serverutils

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        download_id = self.request.path.split("/")[-1]
        if download_id in downloads:
            downloads[download_id].get(self)
        else:
            self.set_status(404, "Unknown download ID %s (existing: %s)" % (download_id, ",".join(str(key) for key in downloads.keys())))

def downloadify(server):
    if not hasattr(server, "bokeh_garden_download"):
        server.bokeh_garden_download = True
        server.add_handlers(r".*", [
            tornado.web.URLSpec(r"/bokeh-garden/download/.*", MainHandler, name="bokeh-garden-download"),
        ])

downloads = weakref.WeakValueDictionary()

class Download(serverutils.HTTPModel, bokeh.models.Div):
    __view_model__ = bokeh.models.Div.__view_model__
    __view_module__ = bokeh.models.Div.__view_module__
    __subtype__ = "Download"

    content = bokeh.core.properties.Any(serialized=False)
    filename = bokeh.core.properties.String(default="file.txt", serialized=False)

    def __init__(self, **kw):
        bokeh.models.Div.__init__(self, **kw)
        self._download_id = None
        
    def http_init(self):
        downloadify(self.bokeh_tornado)
        self._download_id = str(uuid.uuid4())
        downloads[self._download_id] = self
        self.text = "<a href='%s%s/%s' target='_new'>%s</a>" % (self.base_url, "/bokeh-garden/download", self._download_id, self.text)

    def get(self, request_handler):
        request_handler.add_header("Content-Disposition", 'attachment; filename="%s"' % self.filename)
        request_handler.write(bytes(self.content))

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
import os.path
from . import serverutils
import traceback

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            download_id = self.request.path.split("/")[-1]

            path = self.request.path
            path = path.split("bokeh-garden/download/")[1]
            if "/" in path:
                download_id, path = path.split("/", 1)
            else:
                download_id = path
                path = ""
            path = "/" + path

            if download_id in downloads:
                downloads[download_id].get(self, path)
            else:
                self.set_status(404, "Unknown download ID %s (existing: %s)" % (download_id, ",".join(str(key) for key in downloads.keys())))
        except Exception as e:
            print(e)
            traceback.print_exc()

def _downloadify(server):
    if not hasattr(server, "bokeh_garden_download"):
        server.bokeh_garden_download = True
        server.add_handlers(r".*", [
            tornado.web.URLSpec(r"/bokeh-garden/download/.*", MainHandler, name="bokeh-garden-download"),
        ])
        
downloads = weakref.WeakValueDictionary()

class BaseDownload(serverutils.HTTPModel):
    @property
    def download_id(self):
        if not hasattr(self, "_download_id"):
            self._download_id = str(uuid.uuid4())
        return self._download_id
            
    def http_init(self):
        server = self.bokeh_tornado
        if not hasattr(server, "bokeh_garden_download"):
            server.bokeh_garden_download = True
            server.add_handlers(r".*", [
                tornado.web.URLSpec(r"/bokeh-garden/download/.*", MainHandler, name="bokeh-garden-download"),
            ])            
        downloads[self.download_id] = self

    def make_link(self, path):
        return "/".join((self.base_url, 'bokeh-garden/download', self.download_id, path)).replace("//", "/")

    def get(self, request_handler, path):
        raise NotImplementedError()
    
class Download(BaseDownload, bokeh.models.Div):
    __view_model__ = bokeh.models.Div.__view_model__
    __view_module__ = bokeh.models.Div.__view_module__
    __subtype__ = "Download"

    content = bokeh.core.properties.Any(serialized=False)
    filename = bokeh.core.properties.String(default="file.txt", serialized=False)

    def __init__(self, **kw):
        bokeh.models.Div.__init__(self, **kw)
        
    def http_init(self):
        BaseDownload.http_init(self)
        self.text = "<a href='%s' target='_new'>%s</a>" % (self.make_link(""), self.text)

    def get(self, request_handler, path):
        request_handler.add_header("Content-Disposition", 'attachment; filename="%s"' % self.filename)
        request_handler.write(bytes(self.content))

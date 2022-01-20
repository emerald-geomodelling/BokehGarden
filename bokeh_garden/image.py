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
        image_id = self.request.path.split("/")[-1]
        if image_id in images:
            images[image_id].get(self)
        else:
            self.set_status(404, "Unknown image ID %s (existing: %s)" % (image_id, ",".join(str(key) for key in images.keys())))

def imagify(server):
    if not hasattr(server, "bokeh_garden_image"):
        server.bokeh_garden_image = True
        server.add_handlers(r".*", [
            tornado.web.URLSpec(r"/bokeh-garden/image/.*", MainHandler, name="bokeh-garden-image"),
        ])

images = weakref.WeakValueDictionary()

class FastImage(serverutils.HTTPModel, bokeh.models.ImageURL):
    __view_model__ = bokeh.models.ImageURL.__view_model__
    __view_module__ = bokeh.models.ImageURL.__view_module__
    __subtype__ = "FastImage"

    content = bokeh.core.properties.Any(serialized=False)
    filename = bokeh.core.properties.String(default="file.tif", serialized=False)

    def __init__(self, **kw):
        bokeh.models.ImageURL.__init__(self, **kw)
        self._image_id = None
        
    def http_init(self):
        print("XXXXXXXXXXXXXXXX")
        imagify(self.bokeh_tornado)
        self._image_id = str(uuid.uuid4())
        images[self._image_id] = self
        self.url = ["%s%s/%s" % (self.base_url, "/bokeh-garden/image", self._image_id)]

    def get(self, request_handler):
        request_handler.add_header('Access-Control-Allow-Origin', '*')
        request_handler.add_header("Content-Disposition", 'filename="%s"' % self.filename)
        request_handler.write(bytes(self.content))

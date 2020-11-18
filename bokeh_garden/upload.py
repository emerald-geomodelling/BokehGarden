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
from bokeh.util.compiler import TypeScript

TS_CODE = """
    import * as p from "core/properties"
    import {Widget, WidgetView} from "models/widgets/widget"

    declare function jQuery(...args: any[]): any

    export class UploadView extends WidgetView {
      model: Upload

      protected dialogEl: HTMLInputElement

      connect_signals(): void {
        super.connect_signals()
        this.connect(this.model.change, () => this.render())
        this.connect(this.model.properties.width.change, () => this.render())
      }

      render(): void {
        var self = this;
        if (self.dialogEl == null) {
          self.dialogEl = jQuery(`
             <form method="post" action="${self.model.upload_url}/${self.model.upload_id}" enctype="multipart/form-data" target="_">
               <input class="bokeh-garden-upload-file" name="file" type="file" accept="${self.model.accept}"></file>
               <input class="bokeh-garden-upload-submit" type="submit" style="display: none;"></input>
             <form>
          `)[0]
          jQuery(self.dialogEl).find(".bokeh-garden-upload-file").on('change', function() {
            console.log("XXXXXXXXXXXXXXXXX");
            jQuery(self.dialogEl).find(".bokeh-garden-upload-submit").click()
          })
          self.el.appendChild(self.dialogEl)
        }

        // self.dialogEl.style.width = `${self.model.width}px`
        // self.dialogEl.disabled = self.model.disabled
      }
    }

    export namespace Upload {
      export type Attrs = p.AttrsOf<Props>
      export type Props = Widget.Props & {
        upload_id: p.Property<string | string[]>
        upload_url: p.Property<string | string[]>
        value: p.Property<string | string[]>
        mime_type: p.Property<string | string[]>
        filename: p.Property<string | string[]>
        accept: p.Property<string>
        multiple: p.Property<boolean>
      }
    }

    export interface Upload extends Upload.Attrs {}

    export abstract class Upload extends Widget {
      properties: Upload.Props
      __view_type__: UploadView

      constructor(attrs?: Partial<Upload.Attrs>) {
        super(attrs)
      }

      static init_Upload(): void {
        this.prototype.default_view = UploadView

        this.define<Upload.Props>(({Boolean, String, Array, Or}) => ({
          upload_id:  [ String, "" ],
          upload_url: [ String, "" ],

          value:      [ Or(String, Array(String)), "" ],
          mime_type:  [ Or(String, Array(String)), "" ],
          filename:   [ Or(String, Array(String)), "" ],
          accept:     [ String, "" ],
          multiple:  [ Boolean, false ],
        }))
      }
    }
"""

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        upload_id = self.request.path.split("/")[-1]
        if upload_id in uploads:
            uploads[upload_id].post(self)
        else:
            self.set_status(404, "Unknown upload ID %s (existing: %s)" % (upload_id, ",".join(str(key) for key in uploads.keys())))

def uploadify():
    server = serverutils.current_bokeh_tornado_server()
    if not hasattr(server, "bokeh_garden_upload"):
        server.bokeh_garden_upload = True
        server.add_handlers(r".*", [
            tornado.web.URLSpec(r"/bokeh-garden/upload/.*", MainHandler, name="bokeh-garden-upload"),
        ])
    return server.reverse_url("bokeh-garden-upload").replace("/.*", "")

uploads = weakref.WeakValueDictionary()

class SerializableProperty(property):
    def serializable_value(self, value):
        return value

class Upload(bokeh.models.Widget):
    # __view_model__ = bokeh.models.Widget.__view_model__
    # __view_module__ = bokeh.models.Widget.__view_module__
    # __subtype__ = "Upload"

    upload_id = bokeh.core.properties.String()
    upload_url = bokeh.core.properties.String()

    @SerializableProperty
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new):
        old = self._value
        self._value = new
        self.trigger("value", len(old) if old is not None else None, len(new) if new is not None else None)
        
    mime_type = bokeh.core.properties.String(default="", serialized=False, help="""
    The mime type of the selected file.
    """)

    filename = bokeh.core.properties.String(default="", serialized=False, help="""
    The filename of the selected file.
    The file path is not included as browsers do not allow access to it.
    """)
    
    accept = bokeh.core.properties.String(default="", help="""
    Comma-separated list of standard HTML file input filters that restrict what
    files the user can pick from. Values can be:

    `<file extension>`:
        Specific file extension(s) (e.g: .gif, .jpg, .png, .doc) are pickable

    `audio/*`:
        all sound files are pickable

    `video/*`:
        all video files are pickable

    `image/*`:
        all image files are pickable

    `<media type>`:
        A valid `IANA Media Type`_, with no parameters.

    .. _IANA Media Type: https://www.iana.org/assignments/media-types/media-types.xhtml
    """)

    multiple = bokeh.core.properties.Bool(default=False, help="""
    set multiple=False (default) for single file selection, set multiple=True if
    selection of more than one file at a time should be possible.
    """)
    
    __implementation__ = TypeScript(TS_CODE)
    __javascript__ = ["https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"]
    
    def __init__(self, **kw):
        bokeh.models.Widget.__init__(self, **kw)
        self.upload_url = uploadify()
        self.upload_id = str(uuid.uuid4())
        uploads[self.upload_id] = self
        self._doc = bokeh.plotting.curdoc()
        self._value = None
        
    def post(self, request_handler):
        self._file = request_handler.request.files["file"][0]
        self._doc.add_next_tick_callback(self.handle_post)
        request_handler.write(b"Upload succeeded")
    
    @tornado.gen.coroutine
    def handle_post(self):
        self.value = self._file["body"]
        self.mime_type = self._file["content_type"]
        self.filename = self._file["filename"]
        print("Post handled")

    # Override on_change so that a handler can be set for "value" even
    # though that's not a real property...
    def on_change(self, attr, *callbacks):
        bokeh.util.callback_manager.PropertyCallbackManager.on_change(self, attr, *callbacks)

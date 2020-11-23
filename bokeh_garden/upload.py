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
import hashlib

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
      }

      render(): void {
        var self = this;
        var token: String;
        if (self.dialogEl == null) {
          function getCookie(name: String): String {
            var r = document.cookie.match("(^|\\b)" + name + "=([^;]*)(\\b|$)");
            return r ? r[2] : "";
          }
          token = getCookie("_xsrf");
          self.dialogEl = jQuery(`
             <form
              method="post"
              action="${self.model.upload_url}/${self.model.upload_id}"
              enctype="multipart/form-data"
              target="bokeh-garden-upload-iframe-${self.model.upload_id}">
               <input class="bokeh-garden-upload-file" name="file" type="file" accept="${self.model.accept}"></file>
               <input class="bokeh-garden-upload-submit" type="submit" style="display: none;"></input>
               <input type="hidden" name="_xsrf" value="${token}"></input>
               <iframe
                class="bokeh-garden-upload-iframe"
                name="bokeh-garden-upload-iframe-${self.model.upload_id}"
                src="data:text/html,Intentionally%20left%20empty" style="display: none;"></iframe>
             <form>
          `)[0]
          jQuery(self.dialogEl).find(".bokeh-garden-upload-file").on('change', function() {
            jQuery(self.dialogEl).find(".bokeh-garden-upload-file").css({background: "red"})
            jQuery(self.dialogEl).find(".bokeh-garden-upload-submit").click()
          })
          jQuery(self.dialogEl).find(".bokeh-garden-upload-iframe").on('load', function() {
            jQuery(self.dialogEl).find(".bokeh-garden-upload-file").css({background: "inherit"})
          })

          self.el.appendChild(self.dialogEl)
        }
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

def uploadify(server):
    if not hasattr(server, "bokeh_garden_upload"):
        server.bokeh_garden_upload = True
        server.add_handlers(r".*", [
            tornado.web.URLSpec(r"/bokeh-garden/upload/.*", MainHandler, name="bokeh-garden-upload"),
        ])

uploads = weakref.WeakValueDictionary()

class Upload(serverutils.HTTPModel, bokeh.models.Widget):
    upload_id = bokeh.core.properties.String()
    upload_url = bokeh.core.properties.String()

    value = bokeh.core.properties.String(default="", help="""
    The file content hash
    """)

    @property
    def value_bytes(self):
        return self._value
    
    @value_bytes.setter
    def value_bytes(self, new):
        self._value = new
        self.value = hashlib.sha1(new).hexdigest()
        
    mime_type = bokeh.core.properties.String(default="", help="""
    The mime type of the selected file.
    """)

    filename = bokeh.core.properties.String(default="", help="""
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
        self._value = None

    def http_init(self):
        uploadify(self.bokeh_tornado)
        self.upload_url = self.base_url + "/bokeh-garden/upload/"
        self.upload_id = str(uuid.uuid4())
        uploads[self.upload_id] = self
        
    def post(self, request_handler):
        self._file = request_handler.request.files["file"][0]
        self.document.add_next_tick_callback(self.handle_post)
        request_handler.write(b"Upload succeeded")
    
    @tornado.gen.coroutine
    def handle_post(self):
        self.mime_type = self._file["content_type"]
        self.filename = self._file["filename"]
        self.value_bytes = self._file["body"]
        print("Post handled")

    # Override on_change so that a handler can be set for "value" even
    # though that's not a real property...
    def on_change(self, attr, *callbacks):
        bokeh.util.callback_manager.PropertyCallbackManager.on_change(self, attr, *callbacks)

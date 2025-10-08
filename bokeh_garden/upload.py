# upload.py -
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
import tempfile
import os.path

TS_CODE = """
import * as p from "core/properties"
import {Widget, WidgetView} from "models/widgets/widget"

declare function jQuery(...args: any[]): any

export class UploadView extends WidgetView {
  declare model: Upload

  protected dialogEl: HTMLInputElement

  override connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.change, () => this.render())
  }

  override render(): void {
    var self = this;
    var token: String;
    if (self.dialogEl == null) {
      function getCookie(name: String): String {
        var r = document.cookie.match("(^|\\\\b)" + name + "=([^;]*)(\\\\b|$)");
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
    upload_id: p.Property<string>
    upload_url: p.Property<string>
    value: p.Property<string | string[]>
    mime_type: p.Property<string | string[]>
    filename: p.Property<string | string[]>
    accept: p.Property<string>
    multiple: p.Property<boolean>
  }
}

export interface Upload extends Upload.Attrs {}

export class Upload extends Widget {
  declare properties: Upload.Props
  declare __view_type__: UploadView

  constructor(attrs?: Partial<Upload.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = UploadView

    this.define<Upload.Props>(({Boolean, Str, Array, Or}) => ({
      upload_id:  [ Str, "" ],
      upload_url: [ Str, "" ],

      value:      [ Or(Str, Array(Str)), "" ],
      mime_type:  [ Or(Str, Array(Str)), "" ],
      filename:   [ Or(Str, Array(Str)), "" ],
      accept:     [ Str, "" ],
      multiple:   [ Boolean, false ],
    }))
  }
}
"""


class UploadHandler(tornado.web.RequestHandler):
    def initialize(self, obj):
       self._obj = obj

    @tornado.gen.coroutine
    def post(self, upload_id):
       obj = self._obj()
       if obj is None:
          raise Exception("Upload target does not exist any more")
       if upload_id != obj.upload_id:
          raise Exception("Wrong upload target")

       obj.handle_request(self)


class Upload(bokeh.models.Widget):
    __implementation__ = TypeScript(TS_CODE, file="upload.ts")
    upload_id = bokeh.core.properties.String()
    upload_url = bokeh.core.properties.String()

    value = bokeh.core.properties.Either(bokeh.core.properties.String,
                                bokeh.core.properties.List(bokeh.core.properties.String))
    filename = bokeh.core.properties.Either(bokeh.core.properties.String,
                                  bokeh.core.properties.List(bokeh.core.properties.String))
    mime_type = bokeh.core.properties.Either(bokeh.core.properties.String,
                                   bokeh.core.properties.List(bokeh.core.properties.String))
    accept = bokeh.core.properties.String()
    multiple = bokeh.core.properties.Bool(default=False)

    def __init__(self, document, **kw):
       bokeh.models.Widget.__init__(self, **kw)

       self._file = None
       self._filename = None
       self._mime_type = None
       self.document = document

       self.upload_id = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
       self.upload_url = serverutils.register(UploadHandler, obj=weakref.ref(self))

    def handle_request(self, request_handler):
       if 'file' in request_handler.request.files:
          file = request_handler.request.files['file'][0]
          body = file.get('body', b'')
          filename = file.get('filename', '')
          mime_type = file.get('content_type', 'text/plain')
       else:
          body = b''
          filename = ''
          mime_type = ''

       file = tempfile.TemporaryFile()
       file.write(body)
       file.flush()
       file.seek(0)

       if self._file is not None:
          self._file.close()
       self._file = file
       self._filename = filename
       self._mime_type = mime_type
       self.document.add_next_tick_callback(self.handle_upload)
       request_handler.write(b"Upload succeeded")

    @tornado.gen.coroutine
    def handle_upload(self):
       self.filename = self._filename
       self.mime_type = self._mime_type
       self.value = self._filename
       print("Post handled")

    @property
    def file(self):
       self._file.seek(0)
       return self._file

    @property
    def value_bytes(self):
       # Only do this for small file
       return self.file.read()

    # Override on_change so that a handler can be set for "value" even
    # though that's not a real property...
    def on_change(self, attr, *callbacks):
       bokeh.util.callback_manager.PropertyCallbackManager.on_change(self, attr, *callbacks)

    def __del__(self):
       if self._file is not None:
          self._file.close()

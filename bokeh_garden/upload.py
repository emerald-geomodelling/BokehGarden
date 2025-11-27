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
import type * as p from "core/properties"
import {Widget, WidgetView} from "models/widgets/widget"

export class UploadView extends WidgetView {
  declare model: Upload

  protected dialogEl: HTMLElement | null = null

  override connect_signals(): void {
    super.connect_signals()
  }

  override render(): void {
    super.render()

    if (this.dialogEl == null) {
      const getCookie = (name: string): string => {
        const r = document.cookie.match("(^|\\\\b)" + name + "=([^;]*)(\\\\b|$)")
        return r ? r[2] : ""
      }

      const token = getCookie("_xsrf")

      // Create form element
      const form = document.createElement("form")
      form.method = "post"
      form.action = `${this.model.upload_url}${this.model.upload_id}`
      form.enctype = "multipart/form-data"
      form.target = `bokeh-garden-upload-iframe-${this.model.upload_id}`

      // Create file input
      const fileInput = document.createElement("input")
      fileInput.className = "bokeh-garden-upload-file"
      fileInput.name = "file"
      fileInput.type = "file"
      fileInput.accept = this.model.accept

      // Create submit button (hidden)
      const submitBtn = document.createElement("input")
      submitBtn.className = "bokeh-garden-upload-submit"
      submitBtn.type = "submit"
      submitBtn.style.display = "none"

      // Create XSRF token input
      const xsrfInput = document.createElement("input")
      xsrfInput.type = "hidden"
      xsrfInput.name = "_xsrf"
      xsrfInput.value = token

      // Create iframe for form target
      const iframe = document.createElement("iframe")
      iframe.className = "bokeh-garden-upload-iframe"
      iframe.name = `bokeh-garden-upload-iframe-${this.model.upload_id}`
      iframe.src = "data:text/html,Intentionally%20left%20empty"
      iframe.style.display = "none"

      // Set up event listeners
      fileInput.addEventListener("change", () => {
        fileInput.style.background = "red"
        submitBtn.click()
      })

      iframe.addEventListener("load", () => {
        fileInput.style.background = "inherit"
      })

      // Append all elements to form
      form.appendChild(fileInput)
      form.appendChild(submitBtn)
      form.appendChild(xsrfInput)
      form.appendChild(iframe)

      this.dialogEl = form
      this.shadow_el.appendChild(this.dialogEl)
    }
  }
}

export namespace Upload {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Widget.Props & {
    upload_id: p.Property<string>
    upload_url: p.Property<string>
    value: p.Property<string>
    mime_type: p.Property<string>
    filename: p.Property<string>
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

    this.define<Upload.Props>(({Bool, Str}) => ({
      upload_id:  [ Str, "" ],
      upload_url: [ Str, "" ],
      value:      [ Str, "" ],
      mime_type:  [ Str, "" ],
      filename:   [ Str, "" ],
      accept:     [ Str, "" ],
      multiple:   [ Bool, false ],
    }))
  }
}
"""

import streaming_form_data
import streaming_form_data.targets


@tornado.web.stream_request_body
class MainHandler(tornado.web.RequestHandler):
	def prepare(self, *arg, **kw):
		self.parser = None
		self.request.connection.set_max_body_size(1.0e+12)
		tornado.web.RequestHandler.prepare(self, *arg, **kw)

	def data_received(self, data):
		if self.parser is None:
			self.parser = streaming_form_data.StreamingFormDataParser(headers=self.request.headers)
			self.tempfile = tempfile.mktemp()
			self.file_target = streaming_form_data.targets.FileTarget(self.tempfile)
			self.parser.register('file', self.file_target)
			self.parser.register('_xsrf', streaming_form_data.targets.NullTarget())
		self.parser.data_received(data)

	def post(self):
		f = open(self.tempfile, "rb")
		os.unlink(self.tempfile)
		upload_id = self.request.path.split("/")[-1]
		if upload_id in uploads:
			uploads[upload_id].upload(
				request_handler=self,
				file=f,
				filename=self.file_target.multipart_filename,
				mime_type=self.file_target.multipart_content_type)
		else:
			self.set_status(404, "Unknown upload ID %s (existing: %s)" % (
				upload_id, ",".join(str(key) for key in uploads.keys())))


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

	def __init__(self, **kw):
		bokeh.models.Widget.__init__(self, **kw)
		self._file = None

	def http_init(self):
		uploadify(self.bokeh_tornado)
		self.upload_url = self.base_url + "/bokeh-garden/upload/"
		self.upload_id = str(uuid.uuid4())
		uploads[self.upload_id] = self

	def upload(self, request_handler, file, filename, mime_type):
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

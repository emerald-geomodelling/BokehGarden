import bokeh.io
import bokeh_garden
import pandas as pd
import tempfile
import pygrib
import bokeh.models.sources

class GribContainer(bokeh_garden.application.AppWidget, bokeh.models.sources.DataSource):
    def __init__(self, grib):
        self._grib = grib
    @property
    def grib(self): return self._grib

class GribUpload(bokeh_garden.application.AppWidget, bokeh.models.layouts.Column):
    def __init__(self, app, **kw):
        self._app = app
        self._upload = bokeh_garden.upload.Upload()
        bokeh.models.layouts.Column.__init__(self, self._upload, **kw)
        self._upload.on_change("value", self.file_uploaded)
    def file_uploaded(self, attr, old, new):
        with tempfile.NamedTemporaryFile() as f:
            f.write(self._upload.value_bytes)
            self._app.grib = GribContainer(pygrib.open(f.name))

            
